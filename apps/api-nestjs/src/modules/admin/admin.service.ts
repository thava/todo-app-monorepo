import {
  Injectable,
  NotFoundException,
  BadRequestException,
  ConflictException,
  Inject,
} from '@nestjs/common';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq } from 'drizzle-orm';
import * as schema from '@todo-app/database';
import { users } from '@todo-app/database';
import { DATABASE_CONNECTION } from '../../database/database.module';
import { PasswordService } from '../../common/services/password.service';
import { AuditService } from '../audit/audit.service';
import { UpdateUserDto } from './dto/update-user.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { MergeAccountsResponseDto } from './dto/merge-accounts.dto';

@Injectable()
export class AdminService {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
    private readonly passwordService: PasswordService,
    private readonly auditService: AuditService,
  ) {}

  /**
   * Get all users
   */
  async getAllUsers(): Promise<UserResponseDto[]> {
    const allUsers = await this.db.query.users.findMany({
      orderBy: (users, { desc }) => [desc(users.createdAt)],
    });

    return allUsers.map(user => this.sanitizeUser(user));
  }

  /**
   * Get user by ID
   */
  async getUserById(id: string): Promise<UserResponseDto> {
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, id),
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return this.sanitizeUser(user);
  }

  /**
   * Update user by ID
   */
  async updateUser(id: string, updateUserDto: UpdateUserDto): Promise<UserResponseDto> {
    // Check if user exists
    const existingUser = await this.db.query.users.findFirst({
      where: eq(users.id, id),
    });

    if (!existingUser) {
      throw new NotFoundException('User not found');
    }

    // Prepare update data
    const updateData: any = {};

    // Handle email update (now updates localUsername)
    if (updateUserDto.email) {
      const normalizedUsername = updateUserDto.email.toLowerCase().trim();

      // Check if username is already taken by another user
      const usernameExists = await this.db.query.users.findFirst({
        where: eq(users.localUsername, normalizedUsername),
      });

      if (usernameExists && usernameExists.id !== id) {
        throw new ConflictException('Username already in use by another user');
      }

      updateData.localUsername = normalizedUsername;
    }

    // Handle password update
    if (updateUserDto.password) {
      const userEmail = updateUserDto.email || existingUser.localUsername || '';
      const passwordValidation = this.passwordService.validatePasswordStrength(
        updateUserDto.password,
        userEmail,
      );

      if (!passwordValidation.isValid) {
        throw new BadRequestException({
          message: 'Password does not meet security requirements',
          errors: passwordValidation.errors,
        });
      }

      const passwordHash = await this.passwordService.hashPassword(updateUserDto.password);
      updateData.localPasswordHash = passwordHash;
    }

    // Handle fullName update
    if (updateUserDto.fullName !== undefined) {
      updateData.fullName = updateUserDto.fullName.trim();
    }

    // Handle role update
    if (updateUserDto.role !== undefined) {
      updateData.role = updateUserDto.role;
    }

    // Handle emailVerifiedAt update
    if (updateUserDto.emailVerifiedAt !== undefined) {
      if (updateUserDto.emailVerifiedAt === '' || updateUserDto.emailVerifiedAt === 'null' || updateUserDto.emailVerifiedAt === null) {
        updateData.emailVerifiedAt = null;
      } else if (updateUserDto.emailVerifiedAt === 'now') {
        updateData.emailVerifiedAt = new Date();
      } else if (updateUserDto.emailVerifiedAt) {
        // Try to parse as date
        const date = new Date(updateUserDto.emailVerifiedAt);
        if (isNaN(date.getTime())) {
          throw new BadRequestException('Invalid emailVerifiedAt value. Use empty string, "null", "now", or a valid date.');
        }
        updateData.emailVerifiedAt = date;
      }
    }

    // If no updates, return user as-is
    if (Object.keys(updateData).length === 0) {
      return this.sanitizeUser(existingUser);
    }

    // Perform update
    const [updatedUser] = await this.db
      .update(users)
      .set(updateData)
      .where(eq(users.id, id))
      .returning();

    return this.sanitizeUser(updatedUser);
  }

  /**
   * Delete user by ID
   */
  async deleteUser(id: string): Promise<void> {
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, id),
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    await this.db.delete(users).where(eq(users.id, id));
  }

  /**
   * Merge source user account into destination user account
   * Source account will be deleted after merge
   * Fails if there are overlapping identities
   */
  async mergeAccounts(
    sourceUserId: string,
    destinationUserId: string,
    ipAddress?: string,
    userAgent?: string,
  ): Promise<MergeAccountsResponseDto> {
    // Validate that source and destination are different
    if (sourceUserId === destinationUserId) {
      throw new BadRequestException('Source and destination users must be different');
    }

    // Fetch both users
    const sourceUser = await this.db.query.users.findFirst({
      where: eq(users.id, sourceUserId),
    });

    const destinationUser = await this.db.query.users.findFirst({
      where: eq(users.id, destinationUserId),
    });

    if (!sourceUser) {
      throw new NotFoundException(`Source user not found: ${sourceUserId}`);
    }

    if (!destinationUser) {
      throw new NotFoundException(`Destination user not found: ${destinationUserId}`);
    }

    // Check for overlapping identities
    const conflicts: string[] = [];

    // Check local identity overlap
    const sourceHasLocal = sourceUser.localEnabled && sourceUser.localUsername;
    const destHasLocal = destinationUser.localEnabled && destinationUser.localUsername;
    if (sourceHasLocal && destHasLocal) {
      conflicts.push('local');
    }

    // Check Google identity overlap
    const sourceHasGoogle = !!sourceUser.googleSub;
    const destHasGoogle = !!destinationUser.googleSub;
    if (sourceHasGoogle && destHasGoogle) {
      conflicts.push('google');
    }

    // Check Microsoft identity overlap
    const sourceHasMicrosoft = sourceUser.msOid && sourceUser.msTid;
    const destHasMicrosoft = destinationUser.msOid && destinationUser.msTid;
    if (sourceHasMicrosoft && destHasMicrosoft) {
      conflicts.push('microsoft');
    }

    // If there are overlapping identities, fail the merge
    if (conflicts.length > 0) {
      throw new ConflictException(
        `Cannot merge accounts - overlapping identities: ${conflicts.join(', ')}. ` +
        `Both users have the following identity types linked.`
      );
    }

    // Prepare merge data - only update fields from source if destination doesn't have them
    const mergeData: any = {
      updatedAt: new Date(),
    };

    const mergedIdentities: { local?: boolean; google?: boolean; microsoft?: boolean } = {};

    // Merge local identity
    if (sourceHasLocal && !destHasLocal) {
      mergeData.localEnabled = sourceUser.localEnabled;
      mergeData.localUsername = sourceUser.localUsername;
      mergeData.localPasswordHash = sourceUser.localPasswordHash;
      mergedIdentities.local = true;
    }

    // Merge Google identity
    if (sourceHasGoogle && !destHasGoogle) {
      mergeData.googleSub = sourceUser.googleSub;
      mergeData.googleEmail = sourceUser.googleEmail;
      mergedIdentities.google = true;
    }

    // Merge Microsoft identity
    if (sourceHasMicrosoft && !destHasMicrosoft) {
      mergeData.msOid = sourceUser.msOid;
      mergeData.msTid = sourceUser.msTid;
      mergeData.msEmail = sourceUser.msEmail;
      mergedIdentities.microsoft = true;
    }

    // If destination email is not verified but source is, update verification
    if (!destinationUser.emailVerifiedAt && sourceUser.emailVerifiedAt) {
      mergeData.emailVerifiedAt = sourceUser.emailVerifiedAt;
    }

    // Perform the merge - update destination user with source identities
    await this.db
      .update(users)
      .set(mergeData)
      .where(eq(users.id, destinationUserId));

    // Delete the source user
    await this.db.delete(users).where(eq(users.id, sourceUserId));

    // Log the merge operation
    await this.auditService.logAuth(
      'ACCOUNTS_MERGED',
      destinationUserId,
      {
        sourceUserId,
        destinationUserId,
        mergedIdentities,
        sourceUserEmail: sourceUser.localUsername || sourceUser.googleEmail || sourceUser.msEmail,
        destinationUserEmail: destinationUser.localUsername || destinationUser.googleEmail || destinationUser.msEmail,
      },
      ipAddress,
      userAgent,
    );

    return {
      message: 'Accounts merged successfully',
      destinationUserId,
      mergedIdentities,
    };
  }

  /**
   * Remove sensitive fields from user object
   */
  private sanitizeUser(user: typeof users.$inferSelect): UserResponseDto {
    const userEmail = user.localUsername || user.googleEmail || user.msEmail || '';
    return {
      id: user.id,
      email: userEmail,
      fullName: user.fullName,
      role: user.role,
      emailVerifiedAt: user.emailVerifiedAt,
      localUsername: user.localUsername,
      googleEmail: user.googleEmail,
      msEmail: user.msEmail,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };
  }
}
