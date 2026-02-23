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
    chunkSizeWarningLimit: 1800,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // EditorJS in its own chunk
            if (id.includes('@editorjs')) return 'editorjs';
            // MUI components
            if (id.includes('@mui/x-charts')) return 'charts';
            if (id.includes('@mui')) return 'mui';
            // Icons
            if (id.includes('@tabler/icons-react')) return 'tabler-icons';
            // Animation
            if (id.includes('framer-motion')) return 'framer';
            // Swiper
            if (id.includes('swiper')) return 'swiper';
            // Router
            if (id.includes('react-router') || id.includes('@remix-run')) return 'router';
            // Everything else (React, TinyMCE, etc) in vendor
            return 'vendor';
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
