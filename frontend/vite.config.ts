import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/planning': { target: 'http://localhost:8000', rewrite: (path) => path.replace(/^\/api\/planning/, '/api') },
      '/api/operations': { target: 'http://localhost:8001', rewrite: (path) => path.replace(/^\/api\/operations/, '/api') },
      '/api/analytics': { target: 'http://localhost:8002', rewrite: (path) => path.replace(/^\/api\/analytics/, '/api') },
    },
  },
})
