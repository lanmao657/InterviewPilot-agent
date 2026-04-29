import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AppShell from './AppShell.vue'

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRoute: () => ({ path: '/dashboard' }),
    useRouter: () => ({ push: vi.fn() }),
  }
})

describe('AppShell', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders Chinese sidebar navigation', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true,
        },
      },
    })

    expect(wrapper.text()).toContain('仪表盘')
    expect(wrapper.text()).toContain('简历与 JD')
    expect(wrapper.text()).toContain('题库')
    expect(wrapper.text()).toContain('模拟面试')
    expect(wrapper.text()).toContain('报告')
    expect(wrapper.text()).toContain('设置')
  })
})
