import { Injectable } from '@nestjs/common';
import { hash, verify, Options } from '@node-rs/argon2';

@Injectable()
export class PasswordService {
  private readonly hashingOptions: Options = {
    memoryCost: 19456, // 19 MiB
    timeCost: 2,
    parallelism: 1,
  };

  /**
   * Hash a password using Argon2id
   */
  async hashPassword(password: string): Promise<string> {
    return hash(password, this.hashingOptions);
  }

  /**
   * Verify a password against a hash
   */
  async verifyPassword(hash: string, password: string): Promise<boolean> {
    try {
      return await verify(hash, password, this.hashingOptions);
    } catch (error) {
      // Invalid hash format or verification error
      return false;
    }
  }

  /**
   * Validate password meets security requirements
   */
  validatePasswordStrength(password: string, email?: string): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Minimum length
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    // Character class requirements (at least 3 of 4)
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

    const characterClasses = [
      hasUppercase,
      hasLowercase,
      hasNumber,
      hasSpecial,
    ].filter(Boolean).length;

    if (characterClasses < 3) {
      errors.push(
        'Password must contain at least 3 of: uppercase, lowercase, number, special character',
      );
    }

    // Cannot be same as email
    if (email && password.toLowerCase() === email.toLowerCase()) {
      errors.push('Password cannot be the same as your email');
    }

    // Common password check (basic list)
    const commonPasswords = [
      'password',
      'password123',
      '12345678',
      'qwerty',
      'abc123',
      'monkey',
      '1234567',
      'letmein',
      'trustno1',
      'dragon',
      'baseball',
      'iloveyou',
      'master',
      'sunshine',
      'ashley',
      'bailey',
      'passw0rd',
      'shadow',
      '123123',
      '654321',
    ];

    if (commonPasswords.includes(password.toLowerCase())) {
      errors.push('Password is too common');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}
