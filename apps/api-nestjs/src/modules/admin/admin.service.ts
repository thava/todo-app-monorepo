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
import { UpdateUserDto } from './dto/update-user.dto';
import { UserResponseDto } from './dto/user-response.dto';

@Injectable()
export class AdminService {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
    private readonly passwordService: PasswordService,
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
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };
  }
}
