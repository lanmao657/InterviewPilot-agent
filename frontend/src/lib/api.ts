import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

export type User = { id: number; username: string; name: string; email: string | null; is_anonymous: boolean }
export type TokenPair = { access_token: string; refresh_token: string; token_type: string; user: User }
export type DocumentItem = {
  id: number
  kind: 'resume' | 'job_description'
  filename: string
  summary: Record<string, unknown>
  analysis?: Record<string, unknown> | null
  created_at: string
}
export type PrepPlan = { id: number; title: string; target_role: string; fit_score: number; status: string; roadmap: Record<string, unknown>; created_at: string }
export type Question = { id: number; prep_plan_id: number | null; category: string; difficulty: string; prompt: string; rubric: Record<string, unknown>; created_at: string }
export type InterviewTurn = { id: number; question: string; answer: string; feedback: Record<string, unknown>; score: number; created_at: string }
export type Interview = { id: number; prep_plan_id: number | null; title: string; status: string; current_score: number; turns: InterviewTurn[]; created_at: string }
export type Report = { id: number; interview_id: number; title: string; overall_score: number; content: string; metrics: Record<string, number>; created_at: string }
export type AssistantContext = {
  documents: Array<Record<string, unknown>>
  activePlan: Record<string, unknown> | null
  questionCount: number
  recentInterview: Record<string, unknown> | null
  latestReport: Record<string, unknown> | null
}
export type AssistantMessage = {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  status: 'done' | 'streaming' | 'error'
  metadata: Record<string, unknown>
  created_at: string
  completed_at: string | null
}
export type AssistantConversation = {
  id: number
  title: string
  scope: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
  archived_at: string | null
  messages: AssistantMessage[]
}
export type AssistantChatResponse = {
  answer: string
  context: AssistantContext
  conversation: AssistantConversation
  messages: AssistantMessage[]
}

type RequestOptions = RequestInit & { auth?: boolean }

function formatApiError(data: unknown): string {
  if (!data || typeof data !== 'object' || !('detail' in data)) {
    return '请求失败'
  }
  const detail = (data as { detail?: unknown }).detail
  if (typeof detail === 'string') return detail
  if (!Array.isArray(detail)) return '请求失败'

  const messages = detail
    .map((item) => {
      if (!item || typeof item !== 'object') return ''
      const error = item as { loc?: unknown[]; msg?: unknown }
      const field = error.loc?.at(-1)
      const fieldLabel = field === 'username' ? '用户名' : field === 'password' ? '密码' : ''
      const message = typeof error.msg === 'string' ? error.msg.replace(/^Value error,\s*/, '') : ''
      return fieldLabel && message ? `${fieldLabel}不合规范：${message}` : message
    })
    .filter(Boolean)

  return messages.join('；') || '请求失败'
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const auth = useAuthStore()
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (options.auth !== false && auth.accessToken) {
    headers.set('Authorization', `Bearer ${auth.accessToken}`)
  }
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new Error('无法连接服务器，请确认后端服务已启动')
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(formatApiError(data))
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  register: (payload: { username: string; password: string; email?: string }) =>
    request<TokenPair>('/auth/register', { method: 'POST', body: JSON.stringify(payload), auth: false }),
  login: (payload: { username: string; password: string }) =>
    request<TokenPair>('/auth/login', { method: 'POST', body: JSON.stringify(payload), auth: false }),
  guestLogin: () =>
    request<TokenPair>('/auth/guest', { method: 'POST', auth: false }),
  me: () => request<User>('/auth/me'),
  documents: () => request<DocumentItem[]>('/documents'),
  uploadDocument: (kind: 'resume' | 'job-description', file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<DocumentItem>(`/documents/${kind}`, { method: 'POST', body: form })
  },
  deleteDocument: (id: number) =>
    request<void>(`/documents/${id}`, { method: 'DELETE' }),
  analyzeDocument: (id: number) =>
    request<DocumentItem>(`/documents/${id}/analyze`, { method: 'POST' }),
  createPlan: (payload: { resume_id?: number; job_description_id?: number; title: string; target_role: string }) =>
    request<PrepPlan>('/prep-plans', { method: 'POST', body: JSON.stringify(payload) }),
  plans: () => request<PrepPlan[]>('/prep-plans'),
  generateQuestions: (payload: { prep_plan_id?: number; count: number; focus: string }) =>
    request<Question[]>('/questions/generate', { method: 'POST', body: JSON.stringify(payload) }),
  questions: () => request<Question[]>('/questions'),
  createInterview: (payload: { prep_plan_id?: number; title: string }) =>
    request<Interview>('/interviews', { method: 'POST', body: JSON.stringify(payload) }),
  answer: (id: number, payload: { question: string; answer: string }) =>
    request<Interview>(`/interviews/${id}/answer`, { method: 'POST', body: JSON.stringify(payload) }),
  reports: () => request<Report[]>('/reports'),
  reportTrend: () => request<Array<Record<string, number | string>>>('/reports/trend'),
  createReport: (interviewId: number) => request<Report>(`/reports/${interviewId}`, { method: 'POST' }),
  assistantContext: () => request<AssistantContext>('/assistant/context', { method: 'POST' }),
  assistantConversation: () => request<AssistantConversation>('/assistant/conversation'),
  assistantMessages: (conversationId?: number) => {
    const params = conversationId ? `?conversation_id=${conversationId}` : ''
    return request<AssistantMessage[]>(`/assistant/messages${params}`)
  },
  assistantChat: (payload: { message: string; conversation_id?: number }) =>
    request<AssistantChatResponse>('/assistant/chat', { method: 'POST', body: JSON.stringify(payload) }),
  clearAssistantConversation: () => request<void>('/assistant/conversation', { method: 'DELETE' }),
}

export async function streamApi(path: string, onChunk: (chunk: string) => void): Promise<void> {
  const auth = useAuthStore()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${auth.accessToken}` },
  })
  if (!response.ok || !response.body) {
    throw new Error('流式请求失败')
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const event of events) {
      const isError = event.split('\n').some((item) => item === 'event: error')
      const line = event.split('\n').find((item) => item.startsWith('data: '))
      const chunk = line?.replace('data: ', '')
      if (isError) throw new Error(chunk || '流式请求失败')
      if (chunk && chunk !== '[DONE]') onChunk(chunk)
    }
  }
}
