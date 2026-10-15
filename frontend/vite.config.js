import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { existsSync } from 'node:fs'

const runningInContainer = existsSync('/.dockerenv') || Boolean(process.env.KUBERNETES_SERVICE_HOST)
const serviceUrl = (environmentName, containerUrl, localUrl) =>
  process.env[environmentName] || (runningInContainer ? containerUrl : localUrl)

const handleProxyError = (serviceName) => (proxy) => {
  proxy.on('error', (err, _req, res) => {
    if (res && res.writeHead && !res.headersSent) {
      res.writeHead(503, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({
        detail: `${serviceName} is unavailable. Please verify the backend service is running. (${err.code || err.message})`
      }))
    }
  })
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['localhost', '127.0.0.1', 'ingress-nginx-controller.ingress-nginx.svc.cluster.local'],
    proxy: {
      '/api/dashboard': {
        target: serviceUrl('ANALYTICS_SERVICE_URL', 'http://analytics-service:8002', 'http://127.0.0.1:8002'),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: handleProxyError('Analytics service')
      },
      '/api/history': {
        target: serviceUrl('HISTORY_SERVICE_URL', 'http://history-service:8001', 'http://127.0.0.1:8001'),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: handleProxyError('History service')
      },
      '/api': {
        target: serviceUrl('PREDICTION_SERVICE_URL', 'http://prediction-service:8000', 'http://127.0.0.1:8000'),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: handleProxyError('Prediction service')
      }
    }
  }
})
