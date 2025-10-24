import { IsEmail, IsString, MinLength, MaxLength } from 'class-validator';

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
}
