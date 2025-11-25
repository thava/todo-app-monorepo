/**
 * Auth plugin - runs on client side to initialize auth state
 * This loads the user session from localStorage on app startup
 */
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore();

  // Load user from localStorage on client startup
  if (process.client && !authStore._hasHydrated) {
    await authStore.loadUser();
  }

  // Set up automatic token refresh interval
  if (process.client && authStore.isAuthenticated && authStore.accessToken) {
    // Check token every minute and refresh if needed
    const refreshInterval = setInterval(async () => {
      if (authStore.isAuthenticated && authStore.accessToken) {
        if (shouldRefreshToken(authStore.accessToken)) {
          await authStore.refreshAccessToken();
        }
      } else {
        clearInterval(refreshInterval);
      }
    }, 60000); // Check every minute

    // Clean up on app unmount
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        clearInterval(refreshInterval);
      });
    }
  }
});
