import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/store/useAuth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  { path: '/', redirect: '/chat', meta: { requiresAuth: true } },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const auth = useAuth()
  if (to.meta.requiresAuth && !auth.access) next('/login')
  else next()
})

export default router
