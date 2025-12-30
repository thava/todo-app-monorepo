import { IsEmail, IsString, MinLength, MaxLength, IsOptional, IsIn, IsBoolean } from 'class-validator';
import { Transform } from 'class-transformer';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class UpdateUserDto {
  @ApiPropertyOptional({
    description: 'User email address',
    example: 'user@example.com'
  })
  @IsOptional()
  @IsEmail({}, { message: 'Invalid email format' })
  email?: string;

  @ApiPropertyOptional({
    description: 'User password (minimum 8 characters)',
    example: 'newPassword123',
    minLength: 8,
    maxLength: 128
  })
  @IsOptional()
  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  @MaxLength(128, { message: 'Password must be at most 128 characters long' })
  password?: string;

  @ApiPropertyOptional({
    description: 'User full name',
    example: 'John Doe',
    minLength: 1,
    maxLength: 255
  })
  @IsOptional()
  @IsString()
  @MinLength(1, { message: 'Full name is required' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName?: string;

  @ApiPropertyOptional({
    description: 'User role',
    enum: ['guest', 'admin', 'sysadmin'],
    example: 'guest'
  })
  @IsOptional()
  @IsString()
  @IsIn(['guest', 'admin', 'sysadmin'], { message: 'Role must be guest, admin, or sysadmin' })
  role?: 'guest' | 'admin' | 'sysadmin';

  @ApiPropertyOptional({
    description: 'Email verification timestamp (ISO 8601 format, or null to unverify)',
    example: '2025-01-01T00:00:00.000Z'
  })
  @IsOptional()
  @IsString()
  emailVerifiedAt?: string | null;

  @ApiPropertyOptional({
    description: 'Unlink local account (username/password). Requires at least one other OAuth identity (Google or Microsoft) to be linked.',
    example: true
  })
  @IsOptional()
  @IsBoolean()
  unlinkLocal?: boolean;
}
