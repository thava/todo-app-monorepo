import { IsEmail, IsString, MinLength, MaxLength, IsOptional, IsIn } from 'class-validator';
import { Transform } from 'class-transformer';

export class UpdateUserDto {
  @IsOptional()
  @IsEmail({}, { message: 'Invalid email format' })
  email?: string;

  @IsOptional()
  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  @MaxLength(128, { message: 'Password must be at most 128 characters long' })
  password?: string;

  @IsOptional()
  @IsString()
  @MinLength(1, { message: 'Full name is required' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName?: string;

  @IsOptional()
  @IsString()
  @IsIn(['guest', 'admin', 'sysadmin'], { message: 'Role must be guest, admin, or sysadmin' })
  role?: 'guest' | 'admin' | 'sysadmin';

  @IsOptional()
  @IsString()
  emailVerifiedAt?: string | null;
}
