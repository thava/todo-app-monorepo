import { Injectable, NotFoundException, BadRequestException, Inject } from '@nestjs/common';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq } from 'drizzle-orm';
import * as schema from '@todo-app/database';
import { users } from '@todo-app/database';
import { DATABASE_CONNECTION } from '../../database/database.module';

@Injectable()
export class UsersService {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
  ) {}

  /**
   * Find user by ID
   */
  async findById(id: string) {
    const user = await this.db.query.users.findFirst({
      where: eq(users.id, id),
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Remove sensitive fields
    const { localPasswordHash, ...safeUser } = user;
    return safeUser;
  }

  /**
   * Find user by email
   */
  async findByEmail(email: string) {
    const user = await this.db.query.users.findFirst({
      where: eq(users.localUsername, email.toLowerCase().trim()),
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Remove sensitive fields
    const { localPasswordHash, ...safeUser } = user;
    return safeUser;
  }

  /**
   * Get current user profile
   */
  async getProfile(userId: string) {
    const user = await this.findById(userId);
    const userEmail = user.localUsername || user.googleEmail || user.msEmail || '';
    return {
      id: user.id,
      email: userEmail,
      fullName: user.fullName,
      role: user.role,
      emailVerified: !!user.emailVerifiedAt,
      localUsername: user.localUsername || undefined,
      googleEmail: user.googleEmail || undefined,
      msEmail: user.msEmail || undefined,
    };
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: string, data: { fullName?: string; unlinkLocal?: boolean }) {
    // Prepare update data
    const updateData: any = {
      updatedAt: new Date(),
    };

    // Handle fullName update
    if (data.fullName !== undefined) {
      updateData.fullName = data.fullName;
    }

    // Handle unlinkLocal
    if (data.unlinkLocal === true) {
      // Get current user to check identities
      const currentUser = await this.db.query.users.findFirst({
        where: eq(users.id, userId),
      });

      if (!currentUser) {
        throw new NotFoundException('User not found');
      }

      // Check if user has at least one other identity (Google or Microsoft)
      const hasGoogleIdentity = !!currentUser.googleSub;
      const hasMicrosoftIdentity = currentUser.msOid && currentUser.msTid;

      if (!hasGoogleIdentity && !hasMicrosoftIdentity) {
        throw new BadRequestException(
          'Cannot unlink local account. You must have at least one other authentication method (Google or Microsoft) linked.'
        );
      }

      // Check if local account is already unlinked
      if (!currentUser.localEnabled || !currentUser.localUsername) {
        throw new BadRequestException('Local account is not linked');
      }

      // Unlink local account
      updateData.localEnabled = false;
      updateData.localUsername = null;
      updateData.localPasswordHash = null;
    }

    const [updatedUser] = await this.db
      .update(users)
      .set(updateData)
      .where(eq(users.id, userId))
      .returning();

    if (!updatedUser) {
      throw new NotFoundException('User not found');
    }

    // Remove sensitive fields
    const { localPasswordHash, ...safeUser } = updatedUser;
    return safeUser;
  }
}
