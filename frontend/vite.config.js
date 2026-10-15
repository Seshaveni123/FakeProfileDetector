import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['ingress-nginx-controller.ingress-nginx.svc.cluster.local'],
    proxy: {
      '/api/dashboard': {
        target: process.env.ANALYTICS_SERVICE_URL || 'http://analytics-service:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/history': {
        target: process.env.HISTORY_SERVICE_URL || 'http://history-service:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api': {
        target: process.env.PREDICTION_SERVICE_URL || 'http://prediction-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
