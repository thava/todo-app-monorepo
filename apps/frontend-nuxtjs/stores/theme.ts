import { defineStore } from 'pinia';

type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    theme: 'light',
  }),

  actions: {
    /**
     * Initialize theme from localStorage or system preference
     */
    initTheme() {
      if (!process.client) return;

      // Check localStorage first
      const stored = localStorage.getItem('theme') as Theme | null;
      if (stored && (stored === 'light' || stored === 'dark')) {
        this.theme = stored;
        this.applyTheme(stored);
        return;
      }

      // Check system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        this.theme = 'dark';
        this.applyTheme('dark');
      } else {
        this.theme = 'light';
        this.applyTheme('light');
      }
    },

    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
      const newTheme = this.theme === 'light' ? 'dark' : 'light';
      this.setTheme(newTheme);
    },

    /**
     * Set theme explicitly
     */
    setTheme(theme: Theme) {
      this.theme = theme;
      this.applyTheme(theme);

      // Save to localStorage
      if (process.client) {
        localStorage.setItem('theme', theme);
      }
    },

    /**
     * Apply theme to document
     */
    applyTheme(theme: Theme) {
      if (!process.client) return;

      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
    },
  },
});
