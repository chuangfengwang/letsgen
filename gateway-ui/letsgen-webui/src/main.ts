import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'  // Element Plus 样式
import router from './router/index'
import type { Plugin } from 'vue'
import './style.css'  // Tailwind CSS - 放在最后，避免覆盖 Element Plus 样式

const app = createApp(App)

app.use(router)
app.use(ElementPlus as Plugin)

app.mount('#app')
