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
            // TinyMCE in its own chunk - must be loaded after React
            if (id.includes('tinymce') || id.includes('@tinymce')) return 'tinymce';
            // EditorJS in its own chunk
            if (id.includes('@editorjs')) return 'editorjs';
            // MUI components
            if (id.includes('@mui/x-charts')) return 'charts';
            if (id.includes('@mui')) return 'mui';
            // Icons
            if (id.includes('@tabler/icons-react')) return 'tabler-icons';
            // Animation
            if (id.includes('framer-motion')) return 'framer';
            // Everything else including React, React-Router in vendor
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
