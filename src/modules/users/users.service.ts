import { Injectable, NotFoundException, Inject } from '@nestjs/common';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq } from 'drizzle-orm';
import * as schema from '../../database/schema';
import { users } from '../../database/schema';
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
    const { passwordHashPrimary, passwordReversibleDev, ...safeUser } = user;
    return safeUser;
  }

  /**
   * Find user by email
   */
  async findByEmail(email: string) {
    const user = await this.db.query.users.findFirst({
      where: eq(users.email, email.toLowerCase().trim()),
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Remove sensitive fields
    const { passwordHashPrimary, passwordReversibleDev, ...safeUser } = user;
    return safeUser;
  }

  /**
   * Get current user profile
   */
  async getProfile(userId: string) {
    return this.findById(userId);
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: string, data: { fullName?: string }) {
    const [updatedUser] = await this.db
      .update(users)
      .set({
        fullName: data.fullName,
        updatedAt: new Date(),
      })
      .where(eq(users.id, userId))
      .returning();

    if (!updatedUser) {
      throw new NotFoundException('User not found');
    }

    // Remove sensitive fields
    const { passwordHashPrimary, passwordReversibleDev, ...safeUser } =
      updatedUser;
    return safeUser;
  }
}
