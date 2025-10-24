import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Check if running in Docker (VITE_DOCKER env var set to 'true')
const isDocker = process.env.VITE_DOCKER === 'true';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    watch: {
      usePolling: true
    },
    // Only use proxy in Docker mode
    // In local mode, VITE_API_BASE_URL from .env.local is used directly
    proxy: isDocker ? {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true
      }
    } : undefined
  }
});