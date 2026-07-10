import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DashboardPage from './DashboardPage.vue'

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  documents: vi.fn(),
  plans: vi.fn(),
  questions: vi.fn(),
  reports: vi.fn(),
  jdMatch: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mocks.push }),
}))

vi.mock('@/lib/api', () => ({
  api: {
    documents: mocks.documents,
    plans: mocks.plans,
    questions: mocks.questions,
    reports: mocks.reports,
    jdMatch: mocks.jdMatch,
  },
}))

function mountPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return mount(DashboardPage, {
    global: {
      plugins: [createPinia(), [VueQueryPlugin, { queryClient }]],
      stubs: {
        ProgressGuide: true,
        JDKeywords: true,
        JDMatchAnalysis: true,
      },
    },
  })
}

describe('DashboardPage journey guidance', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.documents.mockResolvedValue([])
    mocks.plans.mockResolvedValue([])
    mocks.questions.mockResolvedValue([])
    mocks.reports.mockResolvedValue([])
  })

  it('gives a new user one clear preparation action', async () => {
    const wrapper = mountPage()
    await flushPromises()

    expect(wrapper.text()).toContain('先建立可用的材料底稿')
    expect(wrapper.get('[data-testid="next-action"]').text()).toContain('上传简历与岗位描述')
  })
})
