import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ReportsPage from './ReportsPage.vue'

const mocks = vi.hoisted(() => ({
  reports: vi.fn(),
  reportTrend: vi.fn(),
  plans: vi.fn(),
  answerHistory: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  api: {
    reports: mocks.reports,
    reportTrend: mocks.reportTrend,
    plans: mocks.plans,
    answerHistory: mocks.answerHistory,
  },
}))

vi.mock('@/components/charts/RadarChart.vue', () => ({
  __esModule: true,
  default: { name: 'RadarChart', template: '<div data-test="radar-chart" />' },
}))

vi.mock('@/components/charts/TrendChart.vue', () => ({
  __esModule: true,
  default: { name: 'TrendChart', template: '<div data-test="trend-chart" />' },
}))

function mountPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return mount(ReportsPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
      stubs: {
        ShareCard: true,
        Button: { template: '<button v-bind="$attrs"><slot /></button>' },
      },
    },
  })
}

describe('ReportsPage PDF export', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.reportTrend.mockResolvedValue([])
    mocks.plans.mockResolvedValue([])
    mocks.answerHistory.mockResolvedValue([])
  })

  it('escapes report HTML before writing the printable document', async () => {
    const write = vi.fn()
    const print = vi.fn()
    vi.spyOn(window, 'open').mockReturnValue({
      document: { write, close: vi.fn() },
      print,
    } as unknown as Window)
    mocks.reports.mockResolvedValue([
      {
        id: 1,
        interview_id: 1,
        title: '<img src=x onerror=alert(1)>',
        overall_score: 88,
        content: '<script>alert(1)</script><b>bold</b>',
        metrics: { clarity: 80, structure: 82, evidence: 84, reflection: 86 },
        created_at: '2026-07-06T00:00:00Z',
      },
    ])

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('导出 PDF'))!.trigger('click')

    const html = write.mock.calls[0][0] as string
    expect(html).not.toContain('<script>alert(1)</script>')
    expect(html).not.toContain('<img src=x onerror=alert(1)>')
    expect(html).toContain('&lt;script&gt;alert(1)&lt;/script&gt;')
    expect(html).toContain('&lt;img src=x onerror=alert(1)&gt;')
    expect(print).toHaveBeenCalled()
  })

  it('leads with an actionable conclusion from the weakest score', async () => {
    mocks.reports.mockResolvedValue([
      {
        id: 1,
        interview_id: 1,
        title: '前端模拟面试复盘',
        overall_score: 76,
        content: '继续练习',
        metrics: { clarity: 82, structure: 78, evidence: 61, reflection: 74 },
        created_at: '2026-07-06T00:00:00Z',
      },
    ])

    const wrapper = mountPage()
    await flushPromises()

    expect(wrapper.get('[data-testid="report-insight"]').text()).toContain('下一轮优先补强证据充分度')
  })
})
