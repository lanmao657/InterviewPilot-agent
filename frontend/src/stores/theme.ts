import { defineStore } from 'pinia'

type Theme = 'light' | 'dark' | 'system'

type ThemeState = {
  theme: Theme
  resolved: 'light' | 'dark'
}

function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function resolveTheme(theme: Theme): 'light' | 'dark' {
  return theme === 'system' ? getSystemTheme() : theme
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => {
    const stored = localStorage.getItem('interviewpilot-theme') as Theme | null
    const theme = stored ?? 'system'
    return { theme, resolved: resolveTheme(theme) }
  },
  actions: {
    setTheme(theme: Theme) {
      this.theme = theme
      this.resolved = resolveTheme(theme)
      localStorage.setItem('interviewpilot-theme', theme)
      this.applyTheme()
    },
    toggleTheme() {
      const next = this.resolved === 'dark' ? 'light' : 'dark'
      this.setTheme(next)
    },
    applyTheme() {
      const html = document.documentElement
      if (this.resolved === 'dark') {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },
    initSystemListener() {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      media.addEventListener('change', () => {
        if (this.theme === 'system') {
          this.resolved = getSystemTheme()
          this.applyTheme()
        }
      })
      this.applyTheme()
    },
  },
})
