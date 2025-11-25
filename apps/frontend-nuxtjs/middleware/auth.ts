/**
 * Auth middleware - protects routes that require authentication
 * Redirects to login if user is not authenticated
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore();

  // Wait for hydration on client side
  if (process.client && !authStore._hasHydrated) {
    await authStore.loadUser();
  }

  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    // Store the intended destination
    const redirect = to.fullPath;

    return navigateTo({
      path: '/login',
      query: redirect !== '/' ? { redirect } : undefined,
    });
  }

  // Ensure token is valid (refresh if needed)
  if (authStore.accessToken) {
    await authStore.ensureValidToken();
  }
});
