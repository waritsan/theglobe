import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Force pre-bundling for known packages that can cause star-export/default resolution issues
  optimizeDeps: {
    include: [
      'react-markdown',
      'rehype-sanitize',
      'i18next',
      'i18next-browser-languagedetector',
      'react-i18next'
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://api:3100',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  // Build configuration for production
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
