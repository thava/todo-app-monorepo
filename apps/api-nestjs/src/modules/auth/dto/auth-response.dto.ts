import { ApiProperty } from '@nestjs/swagger';

class UserInfo {
  @ApiProperty({ description: 'User ID', example: 'uuid-123' })
  id: string;

  @ApiProperty({ description: 'User email', example: 'user@example.com' })
  email: string;

  @ApiProperty({ description: 'User full name', example: 'John Doe' })
  fullName: string;

  @ApiProperty({ description: 'User role', enum: ['guest', 'admin', 'sysadmin'], example: 'guest' })
  role: 'guest' | 'admin' | 'sysadmin';

  @ApiProperty({ description: 'Email verification status', example: true })
  emailVerified: boolean;
}

export class AuthResponseDto {
  @ApiProperty({ description: 'JWT access token', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' })
  accessToken: string;

  @ApiProperty({ description: 'JWT refresh token', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' })
  refreshToken: string;

  @ApiProperty({ description: 'User information', type: UserInfo })
  user: {
    id: string;
    email: string;
    fullName: string;
    role: 'guest' | 'admin' | 'sysadmin';
    emailVerified: boolean;
  };
}
