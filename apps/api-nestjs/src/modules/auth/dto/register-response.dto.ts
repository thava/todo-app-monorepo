import { ApiProperty } from '@nestjs/swagger';

class RegisteredUserInfo {
  @ApiProperty({ description: 'User ID', example: 'uuid-123' })
  id: string;

  @ApiProperty({ description: 'User email', example: 'newuser@example.com' })
  email: string;

  @ApiProperty({ description: 'User full name', example: 'John Doe' })
  fullName: string;

  @ApiProperty({ description: 'User role', enum: ['guest', 'admin', 'sysadmin'], example: 'guest' })
  role: 'guest' | 'admin' | 'sysadmin';

  @ApiProperty({ description: 'Email verification status', example: false })
  emailVerified: boolean;
}

export class RegisterResponseDto {
  @ApiProperty({ description: 'Registered user information', type: RegisteredUserInfo })
  user: {
    id: string;
    email: string;
    fullName: string;
    role: 'guest' | 'admin' | 'sysadmin';
    emailVerified: boolean;
  };
}
