// http.ts — Client Axios avec gestion complète du JWT (access + refresh)
import axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { useAuth } from '@/store/useAuth'

/* ──────────────────────────────────────────────────────────────────────────────
   Vue d’ensemble (timeline)
   -----------------------------------------------------------------------------
   t0:  req#1 ──► 401 Unauthorized (access expiré)
        │
        ├─ isRefreshing=false → lancer refresh() avec refresh_token
        │
   t1:  req#2 ──► 401 (pendant que refresh() est en cours)
        └─ isRefreshing=true → mettre req#2 en file d’attente (pending)
   t2:  req#3 ──► 401 (toujours pendant le refresh)
        └─ isRefreshing=true → mettre req#3 en file d’attente (pending)
        │
   t3:  refresh() OK → nouveau access_token (newToken)
        ├─ vider pending: pour chaque “req en attente” :
        │      - réinjecter Authorization: Bearer newToken
        │      - relancer la requête
        └─ relancer aussi req#1 (la requête d’origine)
   Résultat : 1 seul refresh, toutes les requêtes repartent avec le nouveau token.
   ─────────────────────────────────────────────────────────────────────────── */

/* ──────────────────────────────────────────────────────────────────────────────
   Note: structure d’erreur Axios (AxiosError) — simplifiée
   -----------------------------------------------------------------------------
   error: AxiosError = {
     config: { ... }                     // requête originale (AxiosRequestConfig)
     request: XMLHttpRequest | ...       // request bas niveau (environnement)
     response?: {                        // si le serveur a répondu
       status: number                    // ex: 401
       data: any                         // payload JSON renvoyé par l’API
       headers: Record<string, string>
       config: AxiosRequestConfig
     }
     message: string                     // ex: "Request failed with status code 401"
     code?: string                       // ex: "ERR_BAD_REQUEST"
     name: "AxiosError"
   }
   ─────────────────────────────────────────────────────────────────────────── */

// On étend le type de config Axios pour marquer un retry (éviter boucle infinie)
declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: boolean
  }
}

export const base_url = '/api'

// Instance Axios de l’app
const api = axios.create({
  baseURL: base_url,
  withCredentials: true,
  // ⚠️ Important :
  // En DEV : c’est Vite (vite.config.ts → server.proxy) qui redirige /api vers http://localhost:8000
  // En PROD / PREPROD : c’est Nginx (ou le CDN) qui sert la SPA et proxyfie /api vers Django
  // ⇒ Côté front on reste toujours en URL relative (/api), pas besoin de changer de config
})

// ───────────────────────────────────────────────────────────────────────────────
// Intercepteur de requête : injecte le header Authorization si on a un access
// ───────────────────────────────────────────────────────────────────────────────

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = useAuth()
  const token = auth.access
  if (token) {
    // Normalise headers en AxiosHeaders et pose Authorization
    if (!config.headers) config.headers = new AxiosHeaders()
    ;(config.headers as AxiosHeaders).set('Authorization', `Bearer ${token}`)
  }
  return config
})

// ───────────────────────────────────────────────────────────────────────────────
// Variables partagées pour la gestion du refresh
// ───────────────────────────────────────────────────────────────────────────────
let isRefreshing = false
let pending: Array<(newToken: string) => void> = [] // file d’attente des callbacks

// ───────────────────────────────────────────────────────────────────────────────
// Fonctions explicites pour l’intercepteur de réponse
// ───────────────────────────────────────────────────────────────────────────────

/** Réponse OK (2xx) : on renvoie la réponse telle quelle */
function handleSuccess<T = any>(response: AxiosResponse<T>) {
  return response
}

/** Réponse KO (4xx/5xx, timeouts, réseau, etc.) */
async function handleError(error: AxiosError): Promise<any> {
  const auth = useAuth()
  const original = error.config as AxiosRequestConfig

  // Si on n'a pas de config (cas très rare), on propage l’erreur
  if (!original) {
    return Promise.reject(error)
  }

  const status = error.response?.status
  const is401 = status === 401
  const canRetry = !original._retry && !!auth.refresh

  // Si ce n’est pas un 401 “rafraîchissable”, on propage l’erreur
  if (!is401 || !canRetry) {
    return Promise.reject(error)
  }

  // On marque la requête comme “déjà retentée” pour éviter boucles infinies
  original._retry = true

  // Cas A: aucun refresh en cours → on lance un refresh
  if (!isRefreshing) {
    isRefreshing = true
    try {
      // Ta méthode Pinia fait POST /api/token/refresh/ et remet à jour Authorization
      await auth.refreshToken()

      isRefreshing = false

      // Réveille toutes les requêtes en attente avec le nouveau token
      const newToken = auth.access!
      pending.forEach((cb) => cb(newToken))
      pending = []

      // Rejoue la requête originale avec le nouveau token
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${newToken}`
      return api(original)
    } catch (e) {
      // Échec du refresh → on nettoie, on déconnecte, on propage l’erreur
      isRefreshing = false
      pending = []
      auth.logout()
      return Promise.reject(e)
    }
  }

  // Cas B: un refresh est déjà en cours → on place la requête en file d’attente
  // On renvoie une promesse qui sera résolue quand le refresh en cours finira
  return new Promise((resolve) => {
    pending.push((newToken: string) => {
      // Met à jour le header Authorization de la requête originale
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${newToken}`
      // Relance la requête et résout la promesse avec sa réponse
      resolve(api(original))
    })
  })
}

// ───────────────────────────────────────────────────────────────────────────────
// Intercepteur de réponse (succès/erreur)
// ───────────────────────────────────────────────────────────────────────────────
api.interceptors.response.use(handleSuccess, handleError)

export default api
