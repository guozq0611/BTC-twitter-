import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 或者使用 '0.0.0.0'
    port: 3000, // 你可以指定一个端口号
  },
})
