import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { api } from './api';
import type { User } from './types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  rememberMe: boolean;
  _hasHydrated: boolean;

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string, rememberMe?: boolean) => void;
  clearAuth: () => void;
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;
  register: (email: string, password: string, fullName: string, rememberMe: boolean) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  loadUser: () => Promise<void>;
  setRememberMe: (remember: boolean) => void;
  setHasHydrated: (hasHydrated: boolean) => void;
}

// Custom storage that dynamically selects localStorage or sessionStorage based on rememberMe
const dynamicStorage = {
  getItem: (name: string): string | null => {
    if (typeof window === 'undefined') return null;

    // Check both storages and return whichever has data
    const localData = localStorage.getItem(name);
    const sessionData = sessionStorage.getItem(name);

    return localData || sessionData;
  },
  setItem: (name: string, value: string): void => {
    if (typeof window === 'undefined') return;

    try {
      // Parse to check rememberMe flag
      const parsed = JSON.parse(value);
      const rememberMe = parsed.state?.rememberMe ?? true;
      const refreshToken = parsed.state?.refreshToken;

      // Only write to storage if there's actual auth data
      // This prevents page reloads from clearing storage in other tabs
      if (!refreshToken) {
        // No auth data, don't write anything
        return;
      }

      // Determine current storage location
      const currentInLocal = localStorage.getItem(name) !== null;
      const currentInSession = sessionStorage.getItem(name) !== null;

      // Store in the appropriate location
      if (rememberMe) {
        // Only remove from session if we're switching from session to local
        if (currentInSession && !currentInLocal) {
          sessionStorage.removeItem(name);
        }
        localStorage.setItem(name, value);
      } else {
        // Only remove from local if we're switching from local to session
        if (currentInLocal && !currentInSession) {
          localStorage.removeItem(name);
        }
        sessionStorage.setItem(name, value);
      }
    } catch (error) {
      // Fallback to localStorage if parsing fails
      localStorage.setItem(name, value);
    }
  },
  removeItem: (name: string): void => {
    if (typeof window === 'undefined') return;

    // Remove from both storages
    localStorage.removeItem(name);
    sessionStorage.removeItem(name);
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      rememberMe: true, // Default to true
      _hasHydrated: false,

      setHasHydrated: (hasHydrated) => {
        set({ _hasHydrated: hasHydrated });
      },

      setAuth: (user, accessToken, refreshToken, rememberMe = true) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          rememberMe,
        });
      },

      setRememberMe: (remember) => {
        set({ rememberMe: remember });
      },

      clearAuth: () => {
        // Clear from both storages
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-storage');
          sessionStorage.removeItem('auth-storage');
        }
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      login: async (email: string, password: string, rememberMe: boolean) => {
        set({ isLoading: true });
        try {
          const response = await api.login(email, password);
          get().setAuth(response.user, response.accessToken, response.refreshToken, rememberMe);
        } catch (error) {
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (email: string, password: string, fullName: string, rememberMe: boolean) => {
        set({ isLoading: true });
        try {
          const response = await api.register(email, password, fullName);
          get().setAuth(response.user, response.accessToken, response.refreshToken, rememberMe);
        } catch (error) {
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: async () => {
        const { refreshToken } = get();
        if (refreshToken) {
          try {
            await api.logout(refreshToken);
          } catch (error) {
            console.error('Logout error:', error);
          }
        }
        get().clearAuth();
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().clearAuth();
          return;
        }

        try {
          const response = await api.refreshToken(refreshToken);
          set({
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
          });
        } catch (error) {
          console.error('Token refresh error:', error);
          get().clearAuth();
        }
      },

      loadUser: async () => {
        const { accessToken, refreshToken } = get();

        // If no refresh token, can't restore session
        if (!refreshToken) {
          return;
        }

        set({ isLoading: true });

        try {
          // If we have an access token, try using it first
          if (accessToken) {
            const user = await api.getProfile(accessToken) as User;
            set({ user, isAuthenticated: true });
            return;
          }

          // No access token, use refresh token to get a new one
          await get().refreshAccessToken();
          const newAccessToken = get().accessToken;

          if (newAccessToken) {
            const user = await api.getProfile(newAccessToken) as User;
            set({ user, isAuthenticated: true });
          } else {
            get().clearAuth();
          }
        } catch (error) {
          console.error('Load user error:', error);
          // Try to refresh token as fallback
          try {
            await get().refreshAccessToken();
            const newAccessToken = get().accessToken;
            if (newAccessToken) {
              const user = await api.getProfile(newAccessToken) as User;
              set({ user, isAuthenticated: true });
            } else {
              get().clearAuth();
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            get().clearAuth();
          }
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => dynamicStorage),
      partialize: (state) => ({
        user: state.user,
        refreshToken: state.refreshToken,
        rememberMe: state.rememberMe,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
