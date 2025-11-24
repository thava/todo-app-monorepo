// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({

  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  runtimeConfig: {
    // Public keys exposed to client
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:3000',
      // gtag: process.env.NUXT_PUBLIC_GTAG_ID,
    }
  },
  modules: ['@nuxt/eslint', '@nuxtjs/tailwindcss']
})