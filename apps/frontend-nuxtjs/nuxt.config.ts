// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({

  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // Enable SSR only for SSG build (nuxt generate), no SSR runtime in production
  ssr: true,

  runtimeConfig: {
    // Public keys exposed to client
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:3000',
      // Demo configuration (for development/testing)
      demoDomain: process.env.PUBLIC_DEMO_DOMAIN || '',
      demoPassword: process.env.PUBLIC_DEMO_PASSWORD || '',
      demoUsers: process.env.PUBLIC_DEMO_USERS || '',
    }
  },

  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],

  modules: [
    '@nuxt/eslint',
    '@pinia/nuxt',
    '@vueuse/nuxt'
  ],

  // PostCSS configuration for Tailwind CSS v4
  postcss: {
    plugins: {
      '@tailwindcss/postcss': {},
    },
  },

  // Route rules: SSG for public pages, CSR for protected pages
  routeRules: {
    // Public pages - pre-rendered at build time (SSG)
    '/': { prerender: true },
    '/about': { prerender: true },
    '/login': { prerender: true },
    '/register': { prerender: true },
    '/verify-email': { prerender: true },
    '/forgot-password': { prerender: true },
    '/reset-password': { prerender: true },
    // Protected pages - client-side only (CSR after hydration)
    '/dashboard/**': { ssr: false },
  },

  // TypeScript configuration
  typescript: {
    strict: true,
    typeCheck: false, // Disabled for faster dev server startup
  },

  // App configuration
  app: {
    head: {
      title: 'Todo App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'A modern todo application with authentication' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // CSS configuration
  css: ['~/assets/css/main.css'],

  // Router configuration
  router: {
    options: {
      strict: true
    }
  }
})