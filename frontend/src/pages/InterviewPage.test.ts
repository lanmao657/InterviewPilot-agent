import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import InterviewPage from './InterviewPage.vue'

const mocks = vi.hoisted(() => ({
  plans: vi.fn(),
  questions: vi.fn(),
  createInterview: vi.fn(),
  answer: vi.fn(),
  createReport: vi.fn(),
  streamApi: vi.fn(),
}))

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api')
  return {
    ...actual,
    api: {
      plans: mocks.plans,
      questions: mocks.questions,
      createInterview: mocks.createInterview,
      answer: mocks.answer,
      createReport: mocks.createReport,
    },
    streamApi: mocks.streamApi,
  }
})

function mountPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return mount(InterviewPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
    },
  })
}

describe('InterviewPage AI feedback', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.plans.mockResolvedValue([])
    mocks.questions.mockResolvedValue([
      {
        id: 1,
        prep_plan_id: null,
        category: '项目',
        difficulty: 'medium',
        prompt: '请讲一个项目',
        rubric: {},
        created_at: '2026-07-05T00:00:00Z',
      },
    ])
    mocks.createInterview.mockResolvedValue({
      id: 1,
      prep_plan_id: null,
      title: '文字模拟面试',
      status: 'active',
      current_score: 0,
      turns: [],
      created_at: '2026-07-05T00:00:00Z',
    })
    mocks.streamApi.mockResolvedValue(undefined)
  })

  it('shows a useful error when answer scoring fails', async () => {
    mocks.answer.mockRejectedValue(new Error('AI 评分暂时不可用，请稍后重试'))
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('开始面试'))!.trigger('click')
    await flushPromises()
    await wrapper.find('textarea').setValue('这是我的回答')
    await wrapper.findAll('button').find((button) => button.text().includes('提交回答'))!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('AI 评分暂时不可用，请稍后重试')
  })

  it('shows an AI fallback notice from scoring feedback', async () => {
    mocks.answer.mockResolvedValue({
      id: 1,
      prep_plan_id: null,
      title: '文字模拟面试',
      status: 'active',
      current_score: 70,
      turns: [
        {
          id: 1,
          question: '请讲一个项目',
          answer: '这是我的回答',
          score: 70,
          feedback: {
            _ai_notice: 'AI 服务暂时不可用，已使用本地示例结果。',
            summary: '回答已覆盖核心问题',
            dimensions: { clarity: 70, structure: 70, evidence: 70, reflection: 70 },
          },
          created_at: '2026-07-05T00:00:00Z',
        },
      ],
      created_at: '2026-07-05T00:00:00Z',
    })
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('开始面试'))!.trigger('click')
    await flushPromises()
    await wrapper.find('textarea').setValue('这是我的回答')
    await wrapper.findAll('button').find((button) => button.text().includes('提交回答'))!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('AI 服务暂时不可用，已使用本地示例结果。')
  })
})
