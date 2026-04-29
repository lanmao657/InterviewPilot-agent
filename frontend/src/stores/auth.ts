import { defineStore } from 'pinia'

import type { TokenPair, User } from '@/lib/api'

type AuthState = {
  accessToken: string
  refreshToken: string
  user: User | null
}

const stored = localStorage.getItem('interviewpilot-auth')
const initialState = stored ? (JSON.parse(stored) as AuthState) : { accessToken: '', refreshToken: '', user: null }

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => initialState,
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
  },
  actions: {
    setSession(session: TokenPair) {
      this.accessToken = session.access_token
      this.refreshToken = session.refresh_token
      this.user = session.user
      this.persist()
    },
    logout() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      this.persist()
    },
    persist() {
      localStorage.setItem(
        'interviewpilot-auth',
        JSON.stringify({ accessToken: this.accessToken, refreshToken: this.refreshToken, user: this.user }),
      )
    },
  },
})
