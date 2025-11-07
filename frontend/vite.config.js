import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Get base path from environment variable (for GitHub Pages)
// Default to '/' for local development, or '/repository-name/' for GitHub Pages
const base = process.env.VITE_BASE_PATH || '/'

export default defineConfig({
  base: base,
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
