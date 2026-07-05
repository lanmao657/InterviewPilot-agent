import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import QuestionsPage from './QuestionsPage.vue'

const mocks = vi.hoisted(() => ({
  questions: vi.fn(),
  plans: vi.fn(),
  generateQuestions: vi.fn(),
  answerCards: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  api: {
    questions: mocks.questions,
    plans: mocks.plans,
    generateQuestions: mocks.generateQuestions,
    answerCards: mocks.answerCards,
  },
}))

function mountPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return mount(QuestionsPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
      stubs: {
        AnswerCard: true,
      },
    },
  })
}

describe('QuestionsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.questions.mockResolvedValue([])
    mocks.plans.mockResolvedValue([])
    mocks.answerCards.mockResolvedValue([])
  })

  it('shows a useful error when question generation fails', async () => {
    mocks.generateQuestions.mockRejectedValue(new Error('AI 题目生成失败，请稍后重试'))
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('生成题目'))!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('生成失败：AI 题目生成失败，请稍后重试')
  })
})
