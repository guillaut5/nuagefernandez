import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

import { execSync } from 'node:child_process'
import pkg from './package.json' with { type: 'json' }

function safe(cmd: string, fallback = '') {
  try {
    return execSync(cmd).toString().trim()
  } catch {
    return fallback
  }
}

const APP_INFO = {
  name: pkg.name,
  version: pkg.version,
  commit: safe('git rev-parse --short HEAD'),
  branch: safe('git rev-parse --abbrev-ref HEAD'),
  buildDate: new Date().toISOString(),
  repo: 'https://github.com/guillaut5/nuagefernandez', // ⬅️ ici
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  define: {
    __APP_INFO__: JSON.stringify(APP_INFO),
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
