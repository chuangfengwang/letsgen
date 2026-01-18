import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  base: "/ui/",
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      dts: true, // 生成类型声明文件
      imports: ['vue', 'vue-router'], // 自动导入 Vue 和 Vue Router 的 API
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
    tailwindcss(),
    VueI18nPlugin({
      /* 配置选项 */
      // 1. 指定包含翻译信息的资源目录
      include: [path.resolve(__dirname, './src/i18n/locales/**')],
      // 2. 严格模式：如果检测到未使用的翻译 key 会发出警告
      strictMessage: false,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    // 开发环境代理配置（仅开发环境有效）
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
