import { defineStore } from 'pinia'

import { api, streamApi, type AssistantMessage as ApiAssistantMessage } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

export type AssistantMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
  status: 'done' | 'streaming' | 'error'
}

type AssistantState = {
  loadedUserId: number | null
  conversationId: number | null
  messages: AssistantMessage[]
  isStreaming: boolean
  hasLoaded: boolean
  error: string
}

function newId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function mapMessage(message: ApiAssistantMessage): AssistantMessage {
  return {
    id: String(message.id),
    role: message.role,
    content: message.content,
    createdAt: message.created_at,
    status: message.status,
  }
}

export const useAssistantStore = defineStore('assistant', {
  state: (): AssistantState => ({
    loadedUserId: null,
    conversationId: null,
    messages: [],
    isStreaming: false,
    hasLoaded: false,
    error: '',
  }),
  actions: {
    async loadConversation(force = false) {
      const auth = useAuthStore()
      const userId = auth.user?.id ?? null
      if (!auth.accessToken || userId === null) {
        this.loadedUserId = null
        this.conversationId = null
        this.messages = []
        this.hasLoaded = false
        return
      }
      if (this.loadedUserId !== userId) {
        this.loadedUserId = userId
        this.conversationId = null
        this.messages = []
        this.hasLoaded = false
        this.error = ''
      }
      if (this.hasLoaded && !force) return

      const conversation = await api.assistantConversation()
      this.conversationId = conversation.id
      this.messages = conversation.messages.map(mapMessage)
      this.hasLoaded = true
    },
    async clear() {
      try {
        await api.clearAssistantConversation()
      } catch (err) {
        this.error = err instanceof Error ? err.message : '清空聊天失败'
        return
      }
      this.conversationId = null
      this.messages = []
      this.error = ''
      this.hasLoaded = false
      await this.loadConversation(true)
    },
    async send(message: string) {
      const content = message.trim()
      if (!content || this.isStreaming) return

      await this.loadConversation()
      this.error = ''
      this.isStreaming = true
      this.messages.push({ id: newId(), role: 'user', content, createdAt: new Date().toISOString(), status: 'done' })

      const assistantMessage: AssistantMessage = {
        id: newId(),
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
        status: 'streaming',
      }
      this.messages.push(assistantMessage)

      try {
        const params = new URLSearchParams({ message: content })
        if (this.conversationId) params.set('conversation_id', String(this.conversationId))
        await streamApi(`/stream/assistant/chat?${params.toString()}`, (chunk) => {
          assistantMessage.content += chunk
        })
        assistantMessage.status = 'done'
        await this.loadConversation(true)
      } catch (err) {
        assistantMessage.status = 'error'
        assistantMessage.content ||= '助手暂时无法回答，请稍后重试。'
        this.error = err instanceof Error ? err.message : '流式请求失败'
        await this.loadConversation(true).catch(() => undefined)
      } finally {
        this.isStreaming = false
      }
    },
  },
})
