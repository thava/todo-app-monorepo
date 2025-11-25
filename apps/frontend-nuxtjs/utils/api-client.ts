import type { ApiError } from '~/types';

/**
 * Base API Client with error handling and request/response interceptors
 */
export class ApiClient {
  private baseUrl: string;
  private getAccessToken?: () => string | null;
  private onUnauthorized?: () => void;

  constructor(
    baseUrl: string,
    options?: {
      getAccessToken?: () => string | null;
      onUnauthorized?: () => void;
    }
  ) {
    this.baseUrl = baseUrl;
    this.getAccessToken = options?.getAccessToken;
    this.onUnauthorized = options?.onUnauthorized;
  }

  /**
   * Make an API request with error handling
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    useAuth: boolean = false
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    // Build headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if needed
    if (useAuth && this.getAccessToken) {
      const token = this.getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle 401 Unauthorized
      if (response.status === 401) {
        if (this.onUnauthorized) {
          this.onUnauthorized();
        }
        throw await this.parseError(response);
      }

      // Handle other error responses
      if (!response.ok) {
        throw await this.parseError(response);
      }

      // Handle empty responses (204 No Content, etc.)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return undefined as T;
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        return undefined as T;
      }

      return await response.json();
    } catch (error) {
      // Re-throw API errors
      if (this.isApiError(error)) {
        throw error;
      }

      // Handle network errors
      console.error('Network error:', error);
      throw {
        code: 'NETWORK_ERROR',
        message: 'Network error. Please check your connection.',
        statusCode: 0,
      } as ApiError;
    }
  }

  /**
   * Parse error response
   */
  private async parseError(response: Response): Promise<ApiError> {
    try {
      const error = await response.json();
      return {
        code: error.code || 'API_ERROR',
        message: error.message || 'An error occurred',
        details: error.details,
        statusCode: response.status,
      };
    } catch {
      return {
        code: 'API_ERROR',
        message: response.statusText || 'An error occurred',
        statusCode: response.status,
      };
    }
  }

  /**
   * Type guard for API errors
   */
  private isApiError(error: any): error is ApiError {
    return error && typeof error.message === 'string';
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, useAuth: boolean = false): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, useAuth);
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any, useAuth: boolean = false): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
      },
      useAuth
    );
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data: any, useAuth: boolean = false): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      },
      useAuth
    );
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, useAuth: boolean = false): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, useAuth);
  }
}
