import { IsString, IsOptional, MinLength, MaxLength } from 'class-validator';

export class UpdateProfileDto {
  @IsOptional()
  @IsString()
  @MinLength(1, { message: 'Full name cannot be empty' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName?: string;
}
