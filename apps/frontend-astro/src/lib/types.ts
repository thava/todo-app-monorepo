// Shared type definitions

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'guest' | 'admin' | 'sysadmin';
  emailVerified: boolean;
  emailVerifiedAt?: string | null;
  localUsername?: string | null;
  googleEmail?: string | null;
  msEmail?: string | null;
  createdAt?: string;
  updatedAt?: string;
}
