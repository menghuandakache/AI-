import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        // Critical for SSE streaming: disable buffering
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            if (req.url?.includes('/stream')) {
              proxyReq.setHeader('Connection', 'keep-alive')
            }
          })
          proxy.on('proxyRes', (proxyRes, req) => {
            if (req.url?.includes('/stream')) {
              // Disable buffering for streaming responses
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
            }
          })
        },
      },
    },
  },
})
