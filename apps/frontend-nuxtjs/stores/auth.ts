import { defineStore } from 'pinia';
import type { User, LoginDto, RegisterDto } from '~/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  _hasHydrated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    _hasHydrated: false,
  }),

  getters: {
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'sysadmin',
    isSysAdmin: (state) => state.user?.role === 'sysadmin',
    isGuest: (state) => state.user?.role === 'guest',
    hasRole: (state) => (role: string) => state.user?.role === role,
    isEmailVerified: (state) => state.user?.emailVerified || false,
  },

  actions: {
    /**
     * Set authentication data
     */
    setAuth(user: User, accessToken: string, refreshToken: string) {
      this.user = user;
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.isAuthenticated = true;

      // Persist to localStorage
      if (process.client) {
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
      }
    },

    /**
     * Clear authentication data
     */
    clearAuth() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.isAuthenticated = false;

      // Clear from localStorage
      if (process.client) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      }
    },

    /**
     * Login user
     */
    async login(credentials: LoginDto) {
      this.isLoading = true;
      try {
        const api = useApi();
        const response = await api.login(credentials);

        this.setAuth(response.user, response.accessToken, response.refreshToken);

        return response;
      } catch (error) {
        console.error('Login error:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Register new user
     */
    async register(data: RegisterDto) {
      this.isLoading = true;
      try {
        const api = useApi();
        const response = await api.register(data);

        // Note: Register returns RegisterResponseDto which only has user, not tokens
        // User needs to verify email before logging in
        return response;
      } catch (error) {
        console.error('Register error:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Logout user
     */
    async logout() {
      try {
        const api = useApi();
        if (this.refreshToken) {
          await api.logout({ refreshToken: this.refreshToken });
        }
      } catch (error) {
        console.error('Logout error:', error);
        // Continue with logout even if API call fails
      } finally {
        this.clearAuth();
      }
    },

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.clearAuth();
        return false;
      }

      try {
        const api = useApi();
        const response = await api.refreshToken({ refreshToken: this.refreshToken });

        // Update tokens (refresh token is rotating)
        this.accessToken = response.accessToken;
        this.refreshToken = response.refreshToken;
        this.user = response.user;

        // Update localStorage
        if (process.client) {
          localStorage.setItem('accessToken', response.accessToken);
          localStorage.setItem('refreshToken', response.refreshToken);
          localStorage.setItem('user', JSON.stringify(response.user));
        }

        return true;
      } catch (error) {
        console.error('Token refresh error:', error);
        this.clearAuth();
        return false;
      }
    },

    /**
     * Load user from localStorage and validate session
     */
    async loadUser() {
      if (!process.client) return;

      // Try to load from localStorage
      const storedRefreshToken = localStorage.getItem('refreshToken');
      const storedAccessToken = localStorage.getItem('accessToken');
      const storedUser = localStorage.getItem('user');

      if (!storedRefreshToken) {
        this._hasHydrated = true;
        return;
      }

      this.isLoading = true;

      try {
        // Restore state from localStorage
        this.refreshToken = storedRefreshToken;
        this.accessToken = storedAccessToken;
        if (storedUser) {
          this.user = JSON.parse(storedUser);
        }

        // Check if access token is expired or about to expire
        if (!this.accessToken || shouldRefreshToken(this.accessToken)) {
          // Refresh the token
          const refreshed = await this.refreshAccessToken();
          if (!refreshed) {
            this.clearAuth();
            return;
          }
        }

        // Validate session by fetching user profile
        try {
          const api = useApi();
          const user = await api.getProfile();
          this.user = user;
          this.isAuthenticated = true;

          // Update localStorage with fresh user data
          localStorage.setItem('user', JSON.stringify(user));
        } catch (error) {
          // If profile fetch fails, try refreshing token once more
          const refreshed = await this.refreshAccessToken();
          if (refreshed) {
            const user = await api.getProfile();
            this.user = user;
            this.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(user));
          } else {
            this.clearAuth();
          }
        }
      } catch (error) {
        console.error('Load user error:', error);
        this.clearAuth();
      } finally {
        this.isLoading = false;
        this._hasHydrated = true;
      }
    },

    /**
     * Update user profile
     */
    async updateProfile(data: { fullName?: string }) {
      try {
        const api = useApi();
        const updatedUser = await api.updateProfile(data);

        this.user = updatedUser;

        // Update localStorage
        if (process.client) {
          localStorage.setItem('user', JSON.stringify(updatedUser));
        }

        return updatedUser;
      } catch (error) {
        console.error('Update profile error:', error);
        throw error;
      }
    },

    /**
     * Check if token needs refresh and refresh if needed
     */
    async ensureValidToken() {
      if (!this.accessToken) {
        return false;
      }

      // Check if token needs refresh (expires in less than 5 minutes)
      if (shouldRefreshToken(this.accessToken)) {
        return await this.refreshAccessToken();
      }

      return true;
    },
  },
});
