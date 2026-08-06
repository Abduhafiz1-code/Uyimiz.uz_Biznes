import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Django sukut bo'yicha 8000-portda ishlaydi. Boshqa port kerak bo'lsa:
  //   VITE_API_TARGET=http://127.0.0.1:8001 npm run dev
  const target = env.VITE_API_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: 5174,
      proxy: {
        '/api': { target, changeOrigin: true },
        // Yuklangan rasmlar ham bir origin orqali berilsin.
        '/media': { target, changeOrigin: true },
      },
    },
  }
})
