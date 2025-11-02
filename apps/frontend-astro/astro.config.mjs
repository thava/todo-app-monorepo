// @ts-check
import { defineConfig } from 'astro/config';
import path from 'path';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  output: 'static', // Pure SSG mode - no SSR
  integrations: [
    react()
  ],

  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve('./src')
      }
    }
  },

  // Configure server port from environment variable
  server: {
    port: Number(process.env.ASTRO_PORT) || 4200,
    host: true
  }
});