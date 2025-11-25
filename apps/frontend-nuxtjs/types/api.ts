// API Types based on OpenAPI specification

export type UserRole = 'guest' | 'admin' | 'sysadmin';
export type TodoPriority = 'low' | 'medium' | 'high';

// User types
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  emailVerified: boolean;
  emailVerifiedAt?: string | null;
  createdAt?: string;
  updatedAt?: string;
}

// Auth types
export interface LoginDto {
  email: string;
  password: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  fullName: string;
  autoverify?: boolean;
  role?: UserRole;
}

export interface AuthResponseDto {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface RegisterResponseDto {
  user: User;
}

export interface RefreshTokenDto {
  refreshToken: string;
}

export interface RequestPasswordResetDto {
  email: string;
}

export interface ResetPasswordDto {
  token: string;
  newPassword: string;
}

// Todo types
export interface Todo {
  id: string;
  description: string;
  dueDate?: string | null;
  priority?: TodoPriority;
  completed?: boolean;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTodoDto {
  description: string;
  dueDate?: string;
  priority?: TodoPriority;
}

export interface UpdateTodoDto {
  description?: string;
  dueDate?: string | null;
  priority?: TodoPriority;
  completed?: boolean;
}

// Profile types
export interface UpdateProfileDto {
  fullName?: string;
}

// Admin types
export interface UpdateUserDto {
  email?: string;
  password?: string;
  fullName?: string;
  role?: UserRole;
  emailVerifiedAt?: string | null;
}

// API Error types
export interface ApiError {
  code?: string;
  message: string;
  details?: unknown;
  statusCode?: number;
}
