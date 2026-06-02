import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
//路由引入
import router from './router'
//element-plus引入
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/styles/global.scss'
import '@/styles/animations.scss'

const app = createApp(App)


app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
