import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react()],
  css: {
    devSourcemap: true
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  optimizeDeps: {
    esbuildOptions: {
      plugins: [
        {
          name: 'ignore-refractor',
          setup(build) {
            // Ignore refractor imports that aren't actually used
            build.onResolve({ filter: /^refractor\// }, (args) => {
              return { 
                path: args.path, 
                namespace: 'refractor-stub'
              }
            })
            build.onLoad({ filter: /.*/, namespace: 'refractor-stub' }, () => {
              return {
                contents: 'export const refractor = {}; export default {};',
                loader: 'js'
              }
            })
          }
        }
      ]
    }
  },
  build: {
    commonjsOptions: {
      transformMixedEsModules: true
    },
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress refractor warnings
        if (warning.message.includes('refractor')) {
          return
        }
        warn(warning)
      }
    }
  },
})
