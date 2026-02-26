import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import jsconfigPaths from 'vite-jsconfig-paths';

export default defineConfig({
  plugins: [react(), jsconfigPaths()],
  server: {
    port: 4173,
    open: true
  },
  preview: {
    port: 4173
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Large self-contained editors
            if (id.includes('tinymce')) return 'tinymce';
            if (id.includes('@editorjs')) return 'editorjs';
            // MUI is the biggest contributor to the index bundle
            if (id.includes('@mui')) return 'mui';
            // React core + router
            if (
              id.includes('react-dom') ||
              id.includes('react-router') ||
              id.includes('scheduler')
            ) return 'react-vendor';
          }
        },
      },
    },
  },
  optimizeDeps: {
    include: ['tinymce', '@tinymce/tinymce-react']
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
