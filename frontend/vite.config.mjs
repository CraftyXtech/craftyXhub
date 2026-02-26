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
          // Only split out truly self-contained, large packages
          // that don't share dependencies with the rest of the app.
          // Everything else is left to Vite's default splitter.
          if (id.includes('node_modules')) {
            if (id.includes('tinymce')) return 'tinymce';
            if (id.includes('@editorjs')) return 'editorjs';
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
