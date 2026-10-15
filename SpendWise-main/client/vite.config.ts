import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:5000',
      '/budget': 'http://localhost:5000',
      '/users': 'http://localhost:5000',
      '/expenses': 'http://localhost:5000',
      '/income': 'http://localhost:5000',
      '/income_categories': 'http://localhost:5000',
      '/income_frequency': 'http://localhost:5000',
      '/expense_types': 'http://localhost:5000',
      '/savings': 'http://localhost:5000',
      '/api': 'http://localhost:5000',
    },
  },
})
