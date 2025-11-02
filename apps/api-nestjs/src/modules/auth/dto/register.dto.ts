import { IsEmail, IsString, MinLength, MaxLength, IsBoolean, IsOptional, IsIn } from 'class-validator';
import { Transform } from 'class-transformer';

export class RegisterDto {
  @IsEmail({}, { message: 'Invalid email format' })
  email: string;

  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  @MaxLength(128, { message: 'Password must be at most 128 characters long' })
  password: string;

  @IsString()
  @MinLength(1, { message: 'Full name is required' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName: string;

  @IsOptional()
  @IsBoolean()
  @Transform(({ value }) => {
    if (value === 'true') return true;
    if (value === 'false') return false;
    return value;
  })
  autoverify?: boolean = false;

  @IsOptional()
  @IsString()
  @IsIn(['guest', 'admin', 'sysadmin'], { message: 'Role must be guest, admin, or sysadmin' })
  role?: 'guest' | 'admin' | 'sysadmin' = 'guest';
}
