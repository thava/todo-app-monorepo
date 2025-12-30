import { config } from './config';
import type { User } from './types';

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        code: 'UNKNOWN_ERROR',
        message: 'An error occurred',
      }));
      throw error;
    }

    // Handle empty responses (204 No Content, etc.)
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return undefined as T;
    }

    const text = await response.text();
    return text ? JSON.parse(text) : undefined as T;
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{ accessToken: string; refreshToken: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, fullName: string) {
    return this.request<{ accessToken: string; refreshToken: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, fullName }),
    });
  }

  async logout(refreshToken: string) {
    return this.request('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
  }

  async refreshToken(refreshToken: string) {
    return this.request<{ accessToken: string; refreshToken: string }>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
  }

  // User endpoints
  async getProfile(accessToken: string): Promise<User> {
    return this.request<User>('/me', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  // Todo endpoints
  async getTodos(accessToken: string) {
    return this.request('/todos', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  async createTodo(accessToken: string, data: { description: string; priority?: string; dueDate?: string }) {
    return this.request('/todos', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });
  }

  async updateTodo(accessToken: string, id: string, data: { description?: string; priority?: string; dueDate?: string }) {
    return this.request(`/todos/${id}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });
  }

  async deleteTodo(accessToken: string, id: string): Promise<void> {
    await this.request<void>(`/todos/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  // Admin endpoints
  async getUsers(accessToken: string) {
    return this.request('/admin/users', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  async createUser(accessToken: string, data: {
    email: string;
    password: string;
    fullName: string;
    autoverify?: boolean;
    role?: string;
  }) {
    return this.request('/auth/register', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });
  }

  async getUser(accessToken: string, id: string) {
    return this.request(`/admin/users/${id}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  async updateUser(accessToken: string, id: string, data: {
    fullName?: string;
    email?: string;
    role?: string;
    password?: string;
    emailVerifiedAt?: string | null;
  }) {
    return this.request(`/admin/users/${id}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });
  }

  async deleteUser(accessToken: string, id: string): Promise<void> {
    await this.request<void>(`/admin/users/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  // OAuth endpoints
  async unlinkGoogle(accessToken: string): Promise<void> {
    await this.request<void>('/oauth/google/unlink', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  async unlinkMicrosoft(accessToken: string): Promise<void> {
    await this.request<void>('/oauth/microsoft/unlink', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  async mergeAccounts(
    accessToken: string,
    sourceUserId: string,
    destinationUserId: string
  ): Promise<{
    message: string;
    destinationUserId: string;
    mergedIdentities: {
      local?: boolean;
      google?: boolean;
      microsoft?: boolean;
    };
  }> {
    return this.request('/admin/merge-users', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ sourceUserId, destinationUserId }),
    });
  }
}

export const api = new ApiClient(config.apiUrl);
