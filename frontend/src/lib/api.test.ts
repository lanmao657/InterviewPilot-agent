import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { parseSseBlock, streamApi, api } from './api'
import { useAuthStore } from '@/stores/auth'

describe('SSE parsing', () => {
  it('joins multiple data lines while preserving blank lines', () => {
    const event = parseSseBlock('event: message\ndata: 第一段\ndata: \ndata: 第二段')

    expect(event).toEqual({ event: 'message', data: '第一段\n\n第二段' })
  })

  it('marks error events', () => {
    const event = parseSseBlock('event: error\ndata: 流式失败')

    expect(event).toEqual({ event: 'error', data: '流式失败' })
  })

  it('delivers multiline chunks before the done event', async () => {
    setActivePinia(createPinia())
    const chunks: string[] = []
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      'data: 第一段\ndata: \ndata: 第二段\n\nevent: done\ndata: [DONE]\n\n',
      { status: 200, headers: { 'Content-Type': 'text/event-stream' } },
    )))

    try {
      await streamApi('/stream/test', (chunk) => chunks.push(chunk))
    } finally {
      vi.unstubAllGlobals()
    }

    expect(chunks).toEqual(['第一段\n\n第二段'])
  })
})

describe('api auth refresh', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('refreshes an expired access token and retries the original request once', async () => {
    const auth = useAuthStore()
    auth.setSession({
      access_token: 'expired-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      user: { id: 1, username: 'tester', name: 'tester', email: null, is_anonymous: false },
    })

    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: '登录已失效' }), { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        access_token: 'fresh-token',
        refresh_token: 'fresh-refresh-token',
        token_type: 'bearer',
        user: { id: 1, username: 'tester', name: 'tester', email: null, is_anonymous: false },
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        id: 1,
        username: 'tester',
        name: 'tester',
        email: null,
        is_anonymous: false,
      }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)

    const user = await api.me()

    expect(user.username).toBe('tester')
    expect(auth.accessToken).toBe('fresh-token')
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock.mock.calls[2][1].headers.get('Authorization')).toBe('Bearer fresh-token')
  })
})
