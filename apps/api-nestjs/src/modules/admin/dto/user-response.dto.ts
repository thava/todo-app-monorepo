export class UserResponseDto {
  id: string;
  email: string;
  fullName: string;
  role: string;
  emailVerifiedAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}
