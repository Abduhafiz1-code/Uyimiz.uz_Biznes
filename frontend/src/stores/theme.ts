import { defineStore } from 'pinia'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'uyimiz_theme'

function initial(): Theme {
  const saved = localStorage.getItem(STORAGE_KEY) as Theme | null
  if (saved === 'dark' || saved === 'light') return saved
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: initial() as Theme,
  }),
  getters: {
    isDark: (state) => state.theme === 'dark',
    label: (state) => (state.theme === 'dark' ? "Yorug'" : "Qorong'i"),
  },
  actions: {
    apply() {
      document.documentElement.setAttribute('data-theme', this.theme)
      localStorage.setItem(STORAGE_KEY, this.theme)
    },
    toggle() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      this.apply()
    },
    set(theme: Theme) {
      this.theme = theme
      this.apply()
    },
  },
})
