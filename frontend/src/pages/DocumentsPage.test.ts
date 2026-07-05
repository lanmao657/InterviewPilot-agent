import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DocumentsPage from './DocumentsPage.vue'

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  documents: vi.fn(),
  plans: vi.fn(),
  uploadDocument: vi.fn(),
  createPlanStream: vi.fn(),
  deleteDocument: vi.fn(),
  analyzeDocument: vi.fn(),
  rewriteDocument: vi.fn(),
  uploadJDText: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mocks.push }),
}))

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api')
  return {
    ...actual,
    api: {
      documents: mocks.documents,
      plans: mocks.plans,
      uploadDocument: mocks.uploadDocument,
      createPlanStream: mocks.createPlanStream,
      deleteDocument: mocks.deleteDocument,
      analyzeDocument: mocks.analyzeDocument,
      rewriteDocument: mocks.rewriteDocument,
      uploadJDText: mocks.uploadJDText,
    },
  }
})

function mountPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return mount(DocumentsPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
      stubs: {
        ResumeAnalysis: true,
      },
    },
  })
}

describe('DocumentsPage embedding status', () => {
  beforeEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
    mocks.plans.mockResolvedValue([])
    mocks.documents.mockResolvedValue([])
    mocks.uploadDocument.mockResolvedValue({
      id: 9,
      kind: 'resume',
      filename: 'resume.txt',
      summary: { preview: 'resume' },
      analysis: null,
      embedding_status: 'pending',
      embedding_error: null,
      chunk_count: 0,
      created_at: '2026-07-05T00:00:00Z',
    })
  })

  it('shows embedding status and saved failure reason', async () => {
    mocks.documents.mockResolvedValue([
      {
        id: 1,
        kind: 'resume',
        filename: 'resume.txt',
        summary: { preview: 'resume' },
        analysis: null,
        embedding_status: 'processing',
        embedding_error: null,
        chunk_count: 0,
        created_at: '2026-07-05T00:00:00Z',
      },
      {
        id: 2,
        kind: 'job_description',
        filename: 'jd.txt',
        summary: { preview: 'jd' },
        analysis: null,
        embedding_status: 'failed',
        embedding_error: '未解析到可用于索引的文本，请检查文件内容。',
        chunk_count: 0,
        created_at: '2026-07-05T00:00:00Z',
      },
    ])

    const wrapper = mountPage()
    await flushPromises()

    expect(wrapper.text()).toContain('建立中')
    expect(wrapper.text()).toContain('索引失败')
    expect(wrapper.text()).toContain('未解析到可用于索引的文本，请检查文件内容。')
  })

  it('uses indexing copy after uploading a document', async () => {
    const wrapper = mountPage()
    await flushPromises()

    const input = wrapper.find('input[type="file"]')
    const file = new File(['resume'], 'resume.txt', { type: 'text/plain' })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
    await flushPromises()

    expect(wrapper.text()).toContain('上传成功，正在建立语义索引')
  })

  it('blocks plan generation while selected documents are still indexing', async () => {
    mocks.documents.mockResolvedValue([
      {
        id: 1,
        kind: 'resume',
        filename: 'resume.txt',
        summary: { preview: 'resume' },
        analysis: null,
        embedding_status: 'processing',
        embedding_error: null,
        chunk_count: 0,
        created_at: '2026-07-05T00:00:00Z',
      },
    ])
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('生成准备计划'))!.trigger('click')

    expect(wrapper.text()).toContain('文档语义索引仍在建立中，请稍后再试')
    expect(mocks.createPlanStream).not.toHaveBeenCalled()
  })
})
