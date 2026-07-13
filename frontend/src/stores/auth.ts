import { defineStore } from 'pinia'

import type { TokenPair, User } from '@/lib/api'

type AuthState = {
  accessToken: string
  refreshToken: string
  user: User | null
  isGuest: boolean
}

const emptyState: AuthState = { accessToken: '', refreshToken: '', user: null, isGuest: false }

function readInitialState(): AuthState {
  const stored = localStorage.getItem('interviewpilot-auth')
  if (!stored) return emptyState
  try {
    const parsed = JSON.parse(stored) as AuthState
    return { ...parsed, isGuest: parsed.user?.is_anonymous ?? false }
  } catch {
    localStorage.removeItem('interviewpilot-auth')
    return emptyState
  }
}

const initialState: AuthState = readInitialState()

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => initialState,
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
    isGuestUser: (state) => state.isGuest,
  },
  actions: {
    setSession(session: TokenPair, isGuest = false) {
      this.accessToken = session.access_token
      this.refreshToken = session.refresh_token
      this.user = session.user
      this.isGuest = isGuest
      this.persist()
    },
    logout() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      this.isGuest = false
      this.persist()
    },
    persist() {
      localStorage.setItem(
        'interviewpilot-auth',
        JSON.stringify({ accessToken: this.accessToken, refreshToken: this.refreshToken, user: this.user, isGuest: this.isGuest }),
      )
    },
  },
})
