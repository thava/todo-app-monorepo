import { ApiProperty } from '@nestjs/swagger';

class UserInfo {
  @ApiProperty({ description: 'User ID', example: 'uuid-123' })
  id: string;

  @ApiProperty({ description: 'User email (deprecated, use specific identity emails)', example: 'user@example.com' })
  email: string;

  @ApiProperty({ description: 'User full name', example: 'John Doe' })
  fullName: string;

  @ApiProperty({ description: 'User role', enum: ['guest', 'admin', 'sysadmin'], example: 'guest' })
  role: 'guest' | 'admin' | 'sysadmin';

  @ApiProperty({ description: 'Email verification status', example: true })
  emailVerified: boolean;

  @ApiProperty({ description: 'Local username if local identity exists', example: 'john.doe', required: false })
  localUsername?: string;

  @ApiProperty({ description: 'Google email if Google identity is linked', example: 'user@gmail.com', required: false })
  googleEmail?: string;

  @ApiProperty({ description: 'Microsoft email if Microsoft identity is linked', example: 'user@outlook.com', required: false })
  msEmail?: string;
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
    localUsername?: string;
    googleEmail?: string;
    msEmail?: string;
  };
}
