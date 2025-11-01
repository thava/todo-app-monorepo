import { User, Todo, InsertUser, InsertTodo } from '../schema';

/**
 * Public user type - excludes sensitive fields like password hash
 */
export type PublicUser = Omit<User, 'passwordHashPrimary'>;

/**
 * User profile type - includes verification status
 */
export type UserProfile = PublicUser;

/**
 * Todo with owner information
 */
export type TodoWithOwner = Todo & {
  ownerEmail: string;
  ownerName: string;
};

/**
 * Re-export base types for convenience
 */
export type { User, Todo, InsertUser, InsertTodo };

/**
 * Common API response types
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
  timestamp: string;
  path?: string;
  requestId?: string;
}

/**
 * Authentication types
 */
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface AuthResponse extends AuthTokens {
  user: PublicUser;
}

/**
 * User roles enum for type-safe role checks
 */
export enum UserRole {
  GUEST = 'guest',
  ADMIN = 'admin',
  SYSADMIN = 'sysadmin',
}

/**
 * Todo priority enum
 */
export enum TodoPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}
