import {
  Injectable,
  ConflictException,
  UnauthorizedException,
  BadRequestException,
  Inject,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq, and, lt, isNull } from 'drizzle-orm';
import { createHash, randomBytes } from 'crypto';
import * as schema from '@todo-app/database';
import {
  users,
  refreshTokenSessions,
  emailVerificationTokens,
  passwordResetTokens,
} from '@todo-app/database';
import { DATABASE_CONNECTION } from '../../database/database.module';
import { PasswordService } from '../../common/services/password.service';
import { TokenService } from '../../common/services/jwt.service';
import { AuditService } from '../audit/audit.service';
import { EmailService } from '../email/email.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { AuthResponseDto } from './dto/auth-response.dto';
import { RegisterResponseDto } from './dto/register-response.dto';

@Injectable()
export class AuthService {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
    private readonly passwordService: PasswordService,
    private readonly tokenService: TokenService,
    private readonly configService: ConfigService,
    private readonly auditService: AuditService,
    private readonly emailService: EmailService,
  ) {}

  /**
   * Register a new user
   */
  async register(
    registerDto: RegisterDto,
    userAgent?: string,
    ipAddress?: string,
  ): Promise<RegisterResponseDto> {
    const { email, password, fullName, autoverify = false, role = 'guest' } = registerDto;

    // Normalize email (will be used as local username)
    const normalizedUsername = email.toLowerCase().trim();

    // Validate password strength
    const passwordValidation = this.passwordService.validatePasswordStrength(
      password,
      normalizedUsername,
    );

    if (!passwordValidation.isValid) {
      throw new BadRequestException({
        message: 'Password does not meet security requirements',
        errors: passwordValidation.errors,
      });
    }

    // Check if user already exists with this local username
    const existingUser = await this.db.query.users.findFirst({
      where: eq(users.localUsername, normalizedUsername),
    });

    if (existingUser) {
      throw new ConflictException('User with this username already exists');
    }

    // Hash password
    const passwordHash = await this.passwordService.hashPassword(password);

    // Create user with optional autoverify and custom role
    const [newUser] = await this.db
      .insert(users)
      .values({
        localUsername: normalizedUsername,
        fullName: fullName.trim(),
        localPasswordHash: passwordHash,
        localEnabled: true,
        role: role,
        emailVerifiedAt: autoverify ? new Date() : null,
      })
      .returning();

    // Log registration
    await this.auditService.logAuth(
      'REGISTER',
      newUser.id,
      { localUsername: newUser.localUsername, role: newUser.role, autoverified: autoverify },
      ipAddress,
      userAgent,
    );

    // Send verification email only if autoverify is false
    if (!autoverify && newUser.localUsername) {
      await this.sendVerificationEmail(newUser.id, newUser.localUsername, newUser.fullName);
    }

    // Return user info without tokens (email verification required unless autoverified)
    return {
      user: {
        id: newUser.id,
        email: newUser.localUsername || '',
        fullName: newUser.fullName,
        role: newUser.role,
        emailVerified: autoverify,
      },
    };
  }

  /**
   * Login user
   */
  async login(
    loginDto: LoginDto,
    userAgent?: string,
    ipAddress?: string,
  ): Promise<AuthResponseDto> {
    const { email, password } = loginDto;

    // Normalize username
    const normalizedUsername = email.toLowerCase().trim();

    // Find user by local username
    const user = await this.db.query.users.findFirst({
      where: eq(users.localUsername, normalizedUsername),
    });

    if (!user) {
      // Log failed login attempt
      await this.auditService.logAuth(
        'LOGIN_FAILURE',
        undefined,
        { localUsername: normalizedUsername, reason: 'user_not_found' },
        ipAddress,
        userAgent,
      );
      throw new UnauthorizedException('Invalid credentials');
    }

    // Check if local auth is enabled
    if (!user.localEnabled) {
      await this.auditService.logAuth(
        'LOGIN_FAILURE',
        user.id,
        { localUsername: user.localUsername, reason: 'local_auth_disabled' },
        ipAddress,
        userAgent,
      );
      throw new UnauthorizedException('Local authentication is disabled for this user');
    }

    // Verify password
    if (!user.localPasswordHash) {
      await this.auditService.logAuth(
        'LOGIN_FAILURE',
        user.id,
        { localUsername: user.localUsername, reason: 'no_password_set' },
        ipAddress,
        userAgent,
      );
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await this.passwordService.verifyPassword(
      user.localPasswordHash,
      password,
    );

    if (!isPasswordValid) {
      // Log failed login attempt
      await this.auditService.logAuth(
        'LOGIN_FAILURE',
        user.id,
        { localUsername: user.localUsername, reason: 'invalid_password' },
        ipAddress,
        userAgent,
      );
      throw new UnauthorizedException('Invalid credentials');
    }

    // Check if email is verified
    if (!user.emailVerifiedAt) {
      // Log failed login attempt due to unverified email
      await this.auditService.logAuth(
        'LOGIN_FAILURE',
        user.id,
        { localUsername: user.localUsername, reason: 'email_not_verified' },
        ipAddress,
        userAgent,
      );
      throw new UnauthorizedException('Please verify your email address before logging in');
    }

    // Log successful login
    await this.auditService.logAuth(
      'LOGIN_SUCCESS',
      user.id,
      { localUsername: user.localUsername },
      ipAddress,
      userAgent,
    );

    // Generate tokens and create session
    return this.createAuthResponse(user, userAgent, ipAddress);
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken(
    refreshToken: string,
    userAgent?: string,
    ipAddress?: string,
  ): Promise<AuthResponseDto> {
    // Verify refresh token
    let payload;
    try {
      payload = await this.tokenService.verifyRefreshToken(refreshToken);
    } catch (error) {
      throw new UnauthorizedException('Invalid refresh token');
    }

    // Hash the refresh token for lookup
    const tokenHash = this.hashToken(refreshToken);

    // Find session
    const session = await this.db.query.refreshTokenSessions.findFirst({
      where: eq(refreshTokenSessions.refreshTokenHash, tokenHash),
    });

    if (!session) {
      throw new UnauthorizedException('Invalid refresh token');
    }

    // Check if session is revoked
    if (session.revokedAt) {
      throw new UnauthorizedException('Refresh token has been revoked');
    }

    // Check if session is expired
    if (new Date() > session.expiresAt) {
      throw new UnauthorizedException('Refresh token has expired');
    }

    // Get user
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, payload.sub),
    });

    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    // Revoke old refresh token (rotation)
    await this.db
      .update(refreshTokenSessions)
      .set({ revokedAt: new Date() })
      .where(eq(refreshTokenSessions.id, session.id));

    // Log token refresh
    await this.auditService.logAuth(
      'REFRESH_TOKEN_ROTATED',
      user.id,
      { sessionId: session.id },
      ipAddress,
      userAgent,
    );

    // Generate new tokens and create new session
    return this.createAuthResponse(user, userAgent, ipAddress);
  }

  /**
   * Logout (revoke refresh token)
   */
  async logout(refreshToken: string, userId?: string, ipAddress?: string, userAgent?: string): Promise<void> {
    const tokenHash = this.hashToken(refreshToken);

    await this.db
      .update(refreshTokenSessions)
      .set({ revokedAt: new Date() })
      .where(eq(refreshTokenSessions.refreshTokenHash, tokenHash));

    // Log logout
    if (userId) {
      await this.auditService.logAuth(
        'LOGOUT',
        userId,
        {},
        ipAddress,
        userAgent,
      );
    }
  }

  /**
   * Create auth response with tokens and session
   */
  private async createAuthResponse(
    user: typeof users.$inferSelect,
    userAgent?: string,
    ipAddress?: string,
  ): Promise<AuthResponseDto> {
    // Use localUsername as email for backward compatibility, or use google/ms email if available
    const userEmail = user.localUsername || user.googleEmail || user.msEmail || '';

    // Generate access token
    const accessToken = await this.tokenService.generateAccessToken({
      sub: user.id,
      email: userEmail,
      role: user.role,
    });

    // Create refresh token session
    const expiresAt = new Date();
    const expiryDays = 7; // 7 days
    expiresAt.setDate(expiresAt.getDate() + expiryDays);

    const [session] = await this.db
      .insert(refreshTokenSessions)
      .values({
        userId: user.id,
        refreshTokenHash: '', // Will be updated below
        userAgent,
        ipAddress,
        expiresAt,
      })
      .returning();

    // Generate refresh token with session ID
    const refreshToken = await this.tokenService.generateRefreshToken({
      sub: user.id,
      sessionId: session.id,
    });

    // Update session with hashed refresh token
    const tokenHash = this.hashToken(refreshToken);
    await this.db
      .update(refreshTokenSessions)
      .set({ refreshTokenHash: tokenHash })
      .where(eq(refreshTokenSessions.id, session.id));

    return {
      accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: userEmail,
        fullName: user.fullName,
        role: user.role,
        emailVerified: !!user.emailVerifiedAt,
      },
    };
  }

  /**
   * Hash token for storage (SHA-256)
   */
  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  /**
   * Generate a random token (32 bytes, base64url)
   */
  private generateToken(): string {
    return randomBytes(32).toString('base64url');
  }

  /**
   * Send verification email
   */
  private async sendVerificationEmail(
    userId: string,
    email: string,
    fullName: string,
  ): Promise<void> {
    // Generate verification token
    const token = this.generateToken();
    const tokenHash = this.hashToken(token);

    // Set expiry (24 hours)
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    // Store token in database
    await this.db.insert(emailVerificationTokens).values({
      userId,
      tokenHash,
      expiresAt,
    });

    // Send email
    await this.emailService.sendVerificationEmail(email, fullName, token);
  }

  /**
   * Verify email with token
   * Returns a message indicating the result
   */
  async verifyEmail(token: string): Promise<{ message: string; alreadyVerified: boolean }> {
    const tokenHash = this.hashToken(token);

    // First, try to find the token without the verifiedAt filter
    const verificationToken = await this.db.query.emailVerificationTokens.findFirst({
      where: eq(emailVerificationTokens.tokenHash, tokenHash),
    });

    if (!verificationToken) {
      throw new BadRequestException('Invalid verification token');
    }

    // Check if expired first (before checking if already verified)
    if (new Date() > verificationToken.expiresAt) {
      throw new BadRequestException('Verification token has expired');
    }

    // Check if already verified
    if (verificationToken.verifiedAt) {
      return {
        message: 'Email is already verified',
        alreadyVerified: true,
      };
    }

    // Mark token as used
    await this.db
      .update(emailVerificationTokens)
      .set({ verifiedAt: new Date() })
      .where(eq(emailVerificationTokens.id, verificationToken.id));

    // Mark user email as verified
    await this.db
      .update(users)
      .set({ emailVerifiedAt: new Date() })
      .where(eq(users.id, verificationToken.userId));

    return {
      message: 'Email verified successfully',
      alreadyVerified: false,
    };
  }

  /**
   * Resend verification email
   */
  async resendVerificationEmail(userId: string): Promise<void> {
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, userId),
    });

    if (!user) {
      throw new BadRequestException('User not found');
    }

    if (user.emailVerifiedAt) {
      throw new BadRequestException('Email already verified');
    }

    // Delete old verification tokens
    await this.db
      .delete(emailVerificationTokens)
      .where(eq(emailVerificationTokens.userId, userId));

    // Send new verification email
    const userEmail = user.localUsername || user.contactEmail || '';
    await this.sendVerificationEmail(user.id, userEmail, user.fullName);
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    const normalizedUsername = email.toLowerCase().trim();

    // Find user by local username
    const user = await this.db.query.users.findFirst({
      where: eq(users.localUsername, normalizedUsername),
    });

    // Always return success even if user doesn't exist (security best practice)
    if (!user || !user.localEnabled) {
      return;
    }

    // Generate reset token
    const token = this.generateToken();
    const tokenHash = this.hashToken(token);

    // Set expiry (1 hour)
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 1);

    // Delete old reset tokens for this user
    await this.db
      .delete(passwordResetTokens)
      .where(eq(passwordResetTokens.userId, user.id));

    // Store token in database
    await this.db.insert(passwordResetTokens).values({
      userId: user.id,
      tokenHash,
      expiresAt,
    });

    // Send email
    const userEmail = user.localUsername || user.contactEmail || '';
    await this.emailService.sendPasswordResetEmail(userEmail, user.fullName, token);
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    const tokenHash = this.hashToken(token);

    // Find token
    const resetToken = await this.db.query.passwordResetTokens.findFirst({
      where: and(
        eq(passwordResetTokens.tokenHash, tokenHash),
        isNull(passwordResetTokens.usedAt),
      ),
    });

    if (!resetToken) {
      throw new BadRequestException('Invalid or expired reset token');
    }

    // Check if expired
    if (new Date() > resetToken.expiresAt) {
      throw new BadRequestException('Reset token has expired');
    }

    // Get user
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, resetToken.userId),
    });

    if (!user) {
      throw new BadRequestException('User not found');
    }

    // Validate new password
    const userEmail = user.localUsername || user.contactEmail || '';
    const passwordValidation = this.passwordService.validatePasswordStrength(
      newPassword,
      userEmail,
    );

    if (!passwordValidation.isValid) {
      throw new BadRequestException({
        message: 'Password does not meet security requirements',
        errors: passwordValidation.errors,
      });
    }

    // Hash new password
    const passwordHash = await this.passwordService.hashPassword(newPassword);

    // Update user password
    await this.db
      .update(users)
      .set({ localPasswordHash: passwordHash })
      .where(eq(users.id, user.id));

    // Mark token as used
    await this.db
      .update(passwordResetTokens)
      .set({ usedAt: new Date() })
      .where(eq(passwordResetTokens.id, resetToken.id));

    // Revoke all refresh token sessions
    await this.db
      .update(refreshTokenSessions)
      .set({ revokedAt: new Date() })
      .where(eq(refreshTokenSessions.userId, user.id));

    // Send confirmation email
    await this.emailService.sendPasswordChangedEmail(userEmail, user.fullName);
  }
}
