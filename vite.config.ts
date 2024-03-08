import viteCompression from 'vite-plugin-compression'
import vue from '@vitejs/plugin-vue'
import vuetify, {transformAssetUrls} from 'vite-plugin-vuetify'
import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: '@use "./src/assets/styles/global.scss" as *;'
      }
    }
  },
  define: {'process.env': {}},
  plugins: [
    viteCompression(),
    vue({
      template: {transformAssetUrls}
    }),
    vuetify({
      styles: {
        configFile: 'src/assets/styles/settings.scss'
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue'
    ]
  },
  server: {
    port: 8080
  }
})
