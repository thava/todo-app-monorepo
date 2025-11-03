import { IsString, IsOptional, MinLength, MaxLength } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class UpdateProfileDto {
  @ApiPropertyOptional({
    description: 'User full name',
    example: 'Jane Smith',
    minLength: 1,
    maxLength: 255
  })
  @IsOptional()
  @IsString()
  @MinLength(1, { message: 'Full name cannot be empty' })
  @MaxLength(255, { message: 'Full name must be at most 255 characters' })
  fullName?: string;
}
