/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
  ],
  safelist: [
    // Button component classes
    'inline-flex', 'items-center', 'justify-center', 'font-medium', 'rounded-md',
    'transition-colors', 'focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2',
    'disabled:opacity-50', 'disabled:cursor-not-allowed',
    // Button sizes
    'px-3', 'py-1.5', 'text-sm', 'px-4', 'py-2', 'px-6', 'py-3', 'text-base',
    // Button variants
    'bg-primary-600', 'text-white', 'hover:bg-primary-700', 'focus:ring-primary-500',
    'bg-gray-200', 'text-gray-900', 'hover:bg-gray-300', 'focus:ring-gray-500',
    'dark:bg-gray-700', 'dark:text-gray-100', 'dark:hover:bg-gray-600',
    'bg-error-600', 'hover:bg-error-700', 'focus:ring-error-500',
    'bg-transparent', 'text-gray-700', 'hover:bg-gray-100',
    'dark:text-gray-200', 'dark:hover:bg-gray-800',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        success: {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
    },
  },
  plugins: [],
};
