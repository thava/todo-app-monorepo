/**
 * Theme plugin - initializes theme on app startup
 */
export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore();

  // Initialize theme from localStorage or system preference
  if (process.client) {
    themeStore.initTheme();
  }
});
