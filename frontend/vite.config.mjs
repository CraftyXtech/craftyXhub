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
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Large self-contained editors
            if (id.includes('tinymce')) return 'tinymce';
            if (id.includes('@editorjs')) return 'editorjs';
            // React core + router (safe to split — no circular deps)
            if (
              id.includes('react-dom') ||
              id.includes('react-router') ||
              id.includes('scheduler')
            ) return 'react-vendor';
            // UI libraries safely extracted
            if (
              id.includes('framer-motion') ||
              id.includes('swiper') ||
              id.includes('@tabler/icons-react')
            ) return 'ui-vendor';
            // NOTE: Do NOT split @mui — its modules have circular
            // dependencies that break when isolated from the main bundle.
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
