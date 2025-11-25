/**
 * Sysadmin middleware - protects routes that require sysadmin role
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore();

  // Wait for hydration on client side
  if (process.client && !authStore._hasHydrated) {
    await authStore.loadUser();
  }

  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    return navigateTo('/login');
  }

  // Check if user has sysadmin role
  if (!authStore.isSysAdmin) {
    // Redirect to todos page with error message
    return navigateTo('/dashboard/todos');
  }

  // Ensure token is valid
  if (authStore.accessToken) {
    await authStore.ensureValidToken();
  }
});
