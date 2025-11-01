"use client";

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from './api';

interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'guest' | 'admin' | 'sysadmin';
  emailVerified: boolean;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      setAuth: (user, accessToken, refreshToken) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
      },

      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await api.login(email, password);
          get().setAuth(response.user, response.accessToken, response.refreshToken);
        } catch (error) {
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        set({ isLoading: true });
        try {
          const response = await api.register(email, password, fullName);
          get().setAuth(response.user, response.accessToken, response.refreshToken);
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
        if (!accessToken || !refreshToken) {
          return;
        }

        set({ isLoading: true });
        try {
          const user = await api.getProfile(accessToken) as User;
          set({ user, isAuthenticated: true });
        } catch (error) {
          console.error('Load user error:', error);
          // Try to refresh token
          try {
            await get().refreshAccessToken();
            const newAccessToken = get().accessToken;
            if (newAccessToken) {
              const user = await api.getProfile(newAccessToken) as User;
              set({ user, isAuthenticated: true });
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
      partialize: (state) => ({
        refreshToken: state.refreshToken,
      }),
    }
  )
);
