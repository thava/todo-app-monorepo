/**
 * Guest middleware - redirects authenticated users away from guest-only pages
 * Used for login, register pages
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore();

  // Wait for hydration on client side
  if (process.client && !authStore._hasHydrated) {
    await authStore.loadUser();
  }

  // If user is authenticated, redirect to dashboard
  if (authStore.isAuthenticated) {
    return navigateTo('/dashboard/todos');
  }
});
