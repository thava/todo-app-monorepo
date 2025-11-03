import { IsEmail, IsString, MinLength, MaxLength, IsBoolean, IsOptional, IsIn } from 'class-validator';
import { Transform } from 'class-transformer';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class RegisterDto {
  @ApiProperty({
    description: 'User email address',
    example: 'newuser@example.com'
  })
  @IsEmail({}, { message: 'Invalid email format' })
  email: string;

  @ApiProperty({
    description: 'User password (minimum 8 characters)',
    example: 'securePassword123',
    minLength: 8,
    maxLength: 128
  })
  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  @MaxLength(128, { message: 'Password must be at most 128 characters long' })
  password: string;

  @ApiProperty({
    description: 'User full name',
    example: 'John Doe',
    minLength: 1,
    maxLength: 255
  })
  @IsString()
  @MinLength(1, { message: 'Full name is required' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName: string;

  @ApiPropertyOptional({
    description: 'Auto-verify email (for testing purposes)',
    example: false,
    default: false
  })
  @IsOptional()
  @IsBoolean()
  @Transform(({ value }) => {
    if (value === 'true') return true;
    if (value === 'false') return false;
    return value;
  })
  autoverify?: boolean = false;

  @ApiPropertyOptional({
    description: 'User role',
    enum: ['guest', 'admin', 'sysadmin'],
    example: 'guest',
    default: 'guest'
  })
  @IsOptional()
  @IsString()
  @IsIn(['guest', 'admin', 'sysadmin'], { message: 'Role must be guest, admin, or sysadmin' })
  role?: 'guest' | 'admin' | 'sysadmin' = 'guest';
}
