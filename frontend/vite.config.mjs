import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import jsconfigPaths from 'vite-jsconfig-paths';

export default defineConfig({
  plugins: [react(), jsconfigPaths()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('@mui/x-charts')) return 'charts';
            if (id.includes('@mui')) return 'mui';
            if (id.includes('@editorjs')) return 'editorjs';
            if (id.includes('tinymce') || id.includes('@tinymce')) return 'tinymce';
            if (id.includes('@tabler/icons-react')) return 'tabler-icons';
            if (id.includes('framer-motion')) return 'framer';
            if (id.includes('react-router')) return 'react-router';
            if (id.includes('react') || id.includes('react-dom')) return 'react';
            return 'vendor';
          }
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
