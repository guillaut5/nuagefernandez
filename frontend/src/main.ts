import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/main.css' // <-- important pour Tailwind
import { useAuth } from '@/store/useAuth'
import { useMessages } from './store/useMessages'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// Init auth
const auth = useAuth()
auth.initialize()
// Init message
const messStore = useMessages()
messStore.initRealtime()
