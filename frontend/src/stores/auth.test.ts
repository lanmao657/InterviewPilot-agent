import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

describe('auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
    setActivePinia(createPinia())
  })

  it('clears corrupt persisted auth state instead of throwing on startup', async () => {
    localStorage.setItem('interviewpilot-auth', '{bad json')

    const { useAuthStore } = await import('./auth')
    const auth = useAuthStore()

    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
    expect(localStorage.getItem('interviewpilot-auth')).toBeNull()
  })
})
