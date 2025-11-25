import { ApiService } from '~/utils/api';

/**
 * Composable to access the API service
 * This provides a singleton instance of the API service with automatic token management
 */
export const useApi = () => {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();

  // Create API service with token injection and unauthorized handler
  const api = new ApiService(config.public.apiBase, {
    getAccessToken: () => authStore.accessToken,
    onUnauthorized: () => {
      // Clear auth state on 401 responses
      authStore.clearAuth();
      // Redirect to login if not already there
      if (process.client && window.location.pathname !== '/login') {
        navigateTo('/login');
      }
    },
  });

  return api;
};
