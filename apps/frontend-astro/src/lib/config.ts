// Environment configuration
// Note: In Astro, use import.meta.env instead of process.env for client-side code

export const config = {
  // API URL - defaults to localhost:3000 if not set
  apiUrl: import.meta.env.PUBLIC_API_URL || 'http://localhost:3000',

  // Other config values can be added here
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
} as const;
