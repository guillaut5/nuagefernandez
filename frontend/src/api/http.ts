import axios from 'axios'
import { useAuth } from '@/store/useAuth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

// ➜ Intercepteur JWT : ajoute ou renouvelle l’access‑token
api.interceptors.request.use((config) => {
  const auth = useAuth()
  if (auth.access) config.headers.Authorization = `Bearer ${auth.access}`
  return config
})

export default api
