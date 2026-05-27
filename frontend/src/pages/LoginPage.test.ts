import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import LoginPage from './LoginPage.vue'

// 模拟 window.matchMedia，主题 store 初始化时需要
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

describe('LoginPage', () => {
  it('renders the product name and login form', () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $router: { push: () => undefined },
        },
      },
    })

    expect(wrapper.text()).toContain('InterviewPilot')
    expect(wrapper.text()).toContain('用户名或邮箱')
    expect(wrapper.text()).toContain('密码')
  })

  it('shows subtle registration requirements and field-specific validation errors', async () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $router: { push: () => undefined },
        },
      },
    })

    // 找到"没有账号，创建一个"按钮并点击
    const toggleButton = wrapper.findAll('button[type="button"]').find((b) => b.text().includes('没有账号'))
    await toggleButton!.trigger('click')

    expect(wrapper.text()).toContain('3-120 个字符，不能含 @')
    expect(wrapper.text()).toContain('至少 8 位')

    await wrapper.find('input[autocomplete="username"]').setValue('ab')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('用户名不合规范')
  })
})
