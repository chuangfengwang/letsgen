import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import router from './router/index'
import type { Plugin } from 'vue'
import './style.css'

const app = createApp(App)

app.use(router)
app.use(ElementPlus as Plugin)

app.mount('#app')
