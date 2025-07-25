import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/main.css' // <-- important pour Tailwind
import { useAuth } from '@/store/useAuth'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

const auth = useAuth()
auth.initialize()
