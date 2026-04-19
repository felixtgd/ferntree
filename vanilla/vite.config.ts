import { defineConfig } from 'vite';
import { mockApiPlugin } from './mock-plugin';

export default defineConfig({
  plugins: [mockApiPlugin()],
  server: {
    port: 5173,
    host: '0.0.0.0',
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
  },
});
