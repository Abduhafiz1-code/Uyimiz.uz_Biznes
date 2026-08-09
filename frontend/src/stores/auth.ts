import { defineStore } from 'pinia'

import { authApi, TOKEN_KEY } from '@/api/client'
import type { Agent } from '@/types'

/** Agent arizasining holati (backend `certification` maydoni). */
export type CertStatus = 'Kutilmoqda' | 'Tasdiqlangan' | 'Rad etilgan' | 'Bekor qilindi' | ''

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) as string | null,
    agent: null as Agent | null,
    role: '' as string,
    certification: '' as CertStatus,
    loading: false,
    /** Backend SMS'siz test rejimidami — kodni ekranda ko'rsatish uchun. */
    testMode: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    /** CRM'ga faqat tasdiqlangan agent kira oladi. */
    canEnterCrm: (state) => state.role === 'agent' && state.certification === 'Tasdiqlangan',
    isPending: (state) => state.role === 'agent' && state.certification === 'Kutilmoqda',
    isRejected: (state) =>
      state.role === 'agent' &&
      (state.certification === 'Rad etilgan' || state.certification === 'Bekor qilindi'),
  },

  actions: {
    /** 1-bosqich: telefonga tasdiqlash kodi yuborish. */
    async sendCode(phone: string) {
      const { data } = await authApi.post('/send-code', { phone })
      this.testMode = !!data.testMode
      return { demoCode: (data.demoCode as string) || '', testMode: !!data.testMode }
    },

    /**
     * 2-bosqich: kodni tasdiqlash.
     *
     * Kirish har qanday rol uchun ochiq — CRM'ga kirish huquqi keyin
     * `canEnterCrm` bo'yicha hal qilinadi. Shu sababli bu yerda xato
     * tashlamaymiz: agent bo'lmagan foydalanuvchi ariza sahifasiga
     * yo'naltiriladi.
     */
    async verifyCode(phone: string, code: string) {
      const { data } = await authApi.post('/verify', { phone, code })
      this.applySession(data)
      return { role: this.role, canEnterCrm: this.canEnterCrm }
    },

    /** Parol bilan kirish (eski agentlar va admin uchun saqlab qolindi). */
    async login(phone: string, password: string) {
      const { data } = await authApi.post('/login/', { phone, password })
      if (data.role !== 'agent') {
        throw new Error('Bu login Uyimiz Agent panel uchun emas')
      }
      this.applySession(data)
    },

    /** Uyimiz Agent bo'lish uchun ariza topshirish. */
    async applyAsAgent(payload: {
      name: string
      district: string
      email?: string
      historical_deals?: number
    }) {
      const { data } = await authApi.post('/agent-apply', payload)
      this.role = data.role
      this.certification = data.certification
      this.agent = data.user
      return data
    },

    /** Ariza holatini backenddan qayta o'qish. */
    async refreshStatus() {
      if (!this.token) return
      try {
        const { data } = await authApi.get('/agent-apply')
        this.role = data.role
        this.certification = data.certification
        this.agent = data.user
      } catch {
        /* holat o'qilmasa mavjud qiymatlar qoladi */
      }
    },

    async fetchMe() {
      if (!this.token) return
      try {
        const { data } = await authApi.get('/me/')
        this.agent = data
        // /me javobida rol bo'lmasligi mumkin — ariza holatidan aniqlaymiz.
        await this.refreshStatus()
      } catch {
        this.clear()
      }
    },

    applySession(data: { token: string; role?: string; certification?: string; user?: Agent }) {
      this.token = data.token
      this.role = data.role || ''
      this.certification = (data.certification as CertStatus) || ''
      this.agent = data.user || null
      localStorage.setItem(TOKEN_KEY, data.token)
    },

    async logout() {
      try {
        await authApi.post('/logout/')
      } catch {
        /* tarmoq xatosi chiqishga to'sqinlik qilmasin */
      }
      this.clear()
    },

    clear() {
      this.token = null
      this.agent = null
      this.role = ''
      this.certification = ''
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
