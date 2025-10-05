import { defineConfig } from 'vite'

// PUBLIC_INTERFACE
export default defineConfig({
  server: {
    port: 3000,
    strictPort: true
  },
  preview: {
    port: 3000,
    strictPort: true
  }
})
