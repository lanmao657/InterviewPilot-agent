import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/stores/auth'
import LoginPage from './LoginPage.vue'

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  routeQuery: {} as Record<string, string>,
  register: vi.fn(),
  login: vi.fn(),
  guestLogin: vi.fn(),
  convertGuest: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mocks.push }),
  useRoute: () => ({ query: mocks.routeQuery }),
}))

vi.mock('@/lib/api', () => ({
  api: {
    register: mocks.register,
    login: mocks.login,
    guestLogin: mocks.guestLogin,
    convertGuest: mocks.convertGuest,
  },
}))

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
  beforeEach(() => {
    mocks.push.mockReset()
    mocks.register.mockReset()
    mocks.login.mockReset()
    mocks.guestLogin.mockReset()
    mocks.convertGuest.mockReset()
    mocks.routeQuery = {}
    localStorage.clear()
  })

  it('renders the product name and login form', () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [createPinia()],
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

  it('converts a guest account from the registration page', async () => {
    mocks.routeQuery = { mode: 'register', guest: '1' }
    mocks.convertGuest.mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'bearer',
      user: { id: 1, username: 'guest-converted', name: 'guest-converted', email: null, is_anonymous: false },
    })

    const pinia = createPinia()
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [pinia],
      },
    })
    useAuthStore().setSession({
      access_token: 'guest-token',
      refresh_token: 'guest-refresh',
      token_type: 'bearer',
      user: { id: 1, username: 'guest_abc', name: '游客 abc', email: null, is_anonymous: true },
    }, true)

    await wrapper.find('input[autocomplete="username"]').setValue('guest-converted')
    await wrapper.find('input[autocomplete="new-password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(mocks.convertGuest).toHaveBeenCalledWith({ username: 'guest-converted', password: 'password123' })
    expect(mocks.register).not.toHaveBeenCalled()
    expect(mocks.push).toHaveBeenCalledWith('/dashboard')
  })
})
