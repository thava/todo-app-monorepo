import { ApiProperty } from '@nestjs/swagger';

export class UserResponseDto {
  @ApiProperty({ description: 'User ID', example: 'uuid-123' })
  id: string;

  @ApiProperty({ description: 'User email address', example: 'user@example.com' })
  email: string;

  @ApiProperty({ description: 'User full name', example: 'John Doe' })
  fullName: string;

  @ApiProperty({ description: 'User role', example: 'guest' })
  role: string;

  @ApiProperty({ description: 'Email verification timestamp', example: '2025-01-01T00:00:00.000Z', nullable: true })
  emailVerifiedAt: Date | null;

  @ApiProperty({ description: 'User creation timestamp', example: '2025-01-01T00:00:00.000Z' })
  createdAt: Date;

  @ApiProperty({ description: 'User last update timestamp', example: '2025-01-01T00:00:00.000Z' })
  updatedAt: Date;
}
