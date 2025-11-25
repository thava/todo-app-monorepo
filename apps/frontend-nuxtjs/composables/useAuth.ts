/**
 * Composable for authentication
 * Provides easy access to auth state and actions
 */
export const useAuth = () => {
  const authStore = useAuthStore();

  return {
    // State
    user: computed(() => authStore.user),
    accessToken: computed(() => authStore.accessToken),
    refreshToken: computed(() => authStore.refreshToken),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    isLoading: computed(() => authStore.isLoading),
    hasHydrated: computed(() => authStore._hasHydrated),

    // Getters
    isAdmin: computed(() => authStore.isAdmin),
    isSysAdmin: computed(() => authStore.isSysAdmin),
    isGuest: computed(() => authStore.isGuest),
    isEmailVerified: computed(() => authStore.isEmailVerified),
    hasRole: (role: string) => authStore.hasRole(role),

    // Actions
    login: authStore.login,
    register: authStore.register,
    logout: authStore.logout,
    refreshAccessToken: authStore.refreshAccessToken,
    loadUser: authStore.loadUser,
    updateProfile: authStore.updateProfile,
    ensureValidToken: authStore.ensureValidToken,
    clearAuth: authStore.clearAuth,
  };
};
