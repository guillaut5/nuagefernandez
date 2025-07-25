import { defineStore } from 'pinia'
import api from '@/api/http'
import type { TokenPair } from '@/types/api'

interface AuthState {
  access: string | null
  refresh: string | null
  user: { username: string } | null
}

export const useAuth = defineStore('auth', {
  state: (): AuthState => ({
    access: null,
    refresh: null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
  },

  actions: {
    async login(username: string, password: string) {
      const { data } = await api.post<TokenPair>('/api/token/', { username, password })
      this.setTokens(data)
    },

    async refreshToken() {
      if (!this.refresh) return
      try {
        const { data } = await api.post<{ access: string }>('/api/token/refresh/', {
          refresh: this.refresh,
        })
        this.setTokens({ access: data.access, refresh: this.refresh })
      } catch (error) {
        console.error('Erreur lors du rafraîchissement du token :', error)
        this.logout()
      }
    },

    initialize() {
      const saved = localStorage.getItem('tokens')
      if (!saved) return

      try {
        const { access, refresh } = JSON.parse(saved)
        const payload = JSON.parse(atob(access.split('.')[1]))
        const now = Math.floor(Date.now() / 1000)

        if (payload.exp && payload.exp > now) {
          this.setTokens({ access, refresh })
        } else {
          // access expiré, on tente un refresh
          this.refresh = refresh
          this.refreshToken()
        }
      } catch (error) {
        console.warn('Token invalide ou corrompu dans localStorage', error)
        this.logout()
      }
    },

    logout() {
      this.$reset()
      localStorage.removeItem('tokens')
      delete api.defaults.headers.common.Authorization
    },

    setTokens({ access, refresh }: TokenPair) {
      this.access = access
      this.refresh = refresh
      try {
        const payload = JSON.parse(atob(access.split('.')[1]))
        this.user = { username: payload.username }
      } catch (error) {
        console.warn('Erreur de décodage du JWT', error)
        this.user = null
      }

      localStorage.setItem('tokens', JSON.stringify({ access, refresh }))
      api.defaults.headers.common.Authorization = `Bearer ${access}`
    },
  },
})
