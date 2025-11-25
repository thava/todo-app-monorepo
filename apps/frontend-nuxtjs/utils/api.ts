import { ApiClient } from './api-client';
import type {
  LoginDto,
  RegisterDto,
  AuthResponseDto,
  RegisterResponseDto,
  RefreshTokenDto,
  RequestPasswordResetDto,
  ResetPasswordDto,
  User,
  Todo,
  CreateTodoDto,
  UpdateTodoDto,
  UpdateProfileDto,
  UpdateUserDto,
} from '~/types';

/**
 * API Service - handles all API calls
 */
export class ApiService {
  private client: ApiClient;

  constructor(
    baseUrl: string,
    options?: {
      getAccessToken?: () => string | null;
      onUnauthorized?: () => void;
    }
  ) {
    this.client = new ApiClient(baseUrl, options);
  }

  // ==================== Auth Endpoints ====================

  /**
   * Login user
   */
  async login(data: LoginDto): Promise<AuthResponseDto> {
    return this.client.post<AuthResponseDto>('/auth/login', data);
  }

  /**
   * Register new user
   */
  async register(data: RegisterDto): Promise<RegisterResponseDto> {
    return this.client.post<RegisterResponseDto>('/auth/register', data);
  }

  /**
   * Logout user
   */
  async logout(data: RefreshTokenDto): Promise<void> {
    return this.client.post<void>('/auth/logout', data);
  }

  /**
   * Refresh access token
   */
  async refreshToken(data: RefreshTokenDto): Promise<AuthResponseDto> {
    return this.client.post<AuthResponseDto>('/auth/refresh', data);
  }

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<{ message: string }> {
    return this.client.get<{ message: string }>(`/auth/verify-email?token=${token}`);
  }

  /**
   * Resend verification email
   */
  async resendVerification(): Promise<{ message: string }> {
    return this.client.post<{ message: string }>('/auth/resend-verification', undefined, true);
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(data: RequestPasswordResetDto): Promise<{ message: string }> {
    return this.client.post<{ message: string }>('/auth/request-password-reset', data);
  }

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordDto): Promise<{ message: string }> {
    return this.client.post<{ message: string }>('/auth/reset-password', data);
  }

  // ==================== User Endpoints ====================

  /**
   * Get current user profile
   */
  async getProfile(): Promise<User> {
    return this.client.get<User>('/me', true);
  }

  /**
   * Update current user profile
   */
  async updateProfile(data: UpdateProfileDto): Promise<User> {
    return this.client.patch<User>('/me', data, true);
  }

  // ==================== Todo Endpoints ====================

  /**
   * Get all todos
   */
  async getTodos(): Promise<Todo[]> {
    return this.client.get<Todo[]>('/todos', true);
  }

  /**
   * Get a single todo by ID
   */
  async getTodo(id: string): Promise<Todo> {
    return this.client.get<Todo>(`/todos/${id}`, true);
  }

  /**
   * Create a new todo
   */
  async createTodo(data: CreateTodoDto): Promise<Todo> {
    return this.client.post<Todo>('/todos', data, true);
  }

  /**
   * Update a todo
   */
  async updateTodo(id: string, data: UpdateTodoDto): Promise<Todo> {
    return this.client.patch<Todo>(`/todos/${id}`, data, true);
  }

  /**
   * Delete a todo
   */
  async deleteTodo(id: string): Promise<void> {
    return this.client.delete<void>(`/todos/${id}`, true);
  }

  // ==================== Admin Endpoints ====================

  /**
   * Get all users (admin/sysadmin only)
   */
  async getUsers(): Promise<User[]> {
    return this.client.get<User[]>('/admin/users', true);
  }

  /**
   * Get a user by ID (admin/sysadmin only)
   */
  async getUser(id: string): Promise<User> {
    return this.client.get<User>(`/admin/users/${id}`, true);
  }

  /**
   * Update a user (sysadmin only)
   */
  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    return this.client.patch<User>(`/admin/users/${id}`, data, true);
  }

  /**
   * Delete a user (sysadmin only)
   */
  async deleteUser(id: string): Promise<void> {
    return this.client.delete<void>(`/admin/users/${id}`, true);
  }

  /**
   * Create a new user (admin registration)
   */
  async createUser(data: RegisterDto): Promise<RegisterResponseDto> {
    return this.client.post<RegisterResponseDto>('/auth/register', data, true);
  }
}
