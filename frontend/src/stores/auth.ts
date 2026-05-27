import { defineStore } from 'pinia'

import type { TokenPair, User } from '@/lib/api'

type AuthState = {
  accessToken: string
  refreshToken: string
  user: User | null
  isGuest: boolean
}

const stored = localStorage.getItem('interviewpilot-auth')
const initialState: AuthState = stored
  ? (() => {
      const parsed = JSON.parse(stored) as AuthState
      return { ...parsed, isGuest: parsed.user?.is_anonymous ?? false }
    })()
  : { accessToken: '', refreshToken: '', user: null, isGuest: false }

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
