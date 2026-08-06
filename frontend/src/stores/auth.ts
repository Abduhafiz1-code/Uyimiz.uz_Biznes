import { defineStore } from 'pinia'

import api, { TOKEN_KEY } from '@/api/client'
import type { Agent } from '@/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) as string | null,
    agent: null as Agent | null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(phone: string, password: string) {
      const { data } = await api.post('/auth/login/', { phone, password })
      this.token = data.token
      this.agent = data.agent
      localStorage.setItem(TOKEN_KEY, data.token)
    },
    async fetchMe() {
      if (!this.token) return
      try {
        const { data } = await api.get('/auth/me/')
        this.agent = data
      } catch {
        this.clear()
      }
    },
    async logout() {
      try {
        await api.post('/auth/logout/')
      } catch {
        /* tarmoq xatosi chiqishga to'sqinlik qilmasin */
      }
      this.clear()
    },
    clear() {
      this.token = null
      this.agent = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
