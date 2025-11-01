export class AuthResponseDto {
  accessToken: string;
  refreshToken: string;
  user: {
    id: string;
    email: string;
    fullName: string;
    role: 'guest' | 'admin' | 'sysadmin';
    emailVerified: boolean;
  };
}
