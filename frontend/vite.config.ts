import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/sessions': 'http://localhost:8000',
      '/session': 'http://localhost:8000',
    },
  },
});
