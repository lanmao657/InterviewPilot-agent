import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AppShell from './AppShell.vue'
import { useAuthStore } from '@/stores/auth'

const routerPush = vi.hoisted(() => vi.fn())

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRoute: () => ({ path: '/dashboard' }),
    useRouter: () => ({ push: routerPush }),
  }
})

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

describe('AppShell', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    routerPush.mockReset()
  })

  it('groups navigation by the prepare, practice, and review journey', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true,
        },
      },
    })

    expect(wrapper.text()).toContain('概览')
    expect(wrapper.text()).toContain('准备')
    expect(wrapper.text()).toContain('材料工作区')
    expect(wrapper.text()).toContain('训练')
    expect(wrapper.text()).toContain('题库')
    expect(wrapper.text()).toContain('模拟面试')
    expect(wrapper.text()).toContain('复盘')
    expect(wrapper.text()).toContain('能力报告')
    expect(wrapper.text()).toContain('设置')
  })

  it('keeps coaching contextual and exposes reports in mobile navigation', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true,
          GlobalAssistantWidget: true,
          ToastContainer: true,
        },
      },
    })

    expect(wrapper.get('[data-testid="coach-entry"]').text()).toContain('问教练')
    const mobileNav = wrapper.get('[aria-label="移动端主导航"]')
    expect(mobileNav.text()).toContain('报告')
    expect(mobileNav.text()).not.toContain('助手')
    expect(wrapper.find('[aria-label="切换为深色主题"]').exists()).toBe(true)
  })

  it('routes guest registration entry points to guest conversion registration', async () => {
    const auth = useAuthStore()
    auth.setSession({
      access_token: 'guest-token',
      refresh_token: 'guest-refresh',
      token_type: 'bearer',
      user: { id: 1, username: 'guest_abc', name: '游客 abc', email: null, is_anonymous: true },
    }, true)

    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true,
          GlobalAssistantWidget: true,
          ToastContainer: true,
        },
      },
    })

    await wrapper.findAll('button').find((button) => button.text().includes('注册正式账号'))!.trigger('click')
    expect(routerPush).toHaveBeenLastCalledWith('/login?mode=register&guest=1')

    await wrapper.findAll('button').find((button) => button.text().includes('退出登录'))!.trigger('click')
    await wrapper.findAll('button').find((button) => button.text().includes('注册正式账号'))!.trigger('click')
    expect(routerPush).toHaveBeenLastCalledWith('/login?mode=register&guest=1')
  })

  it('moves focus into the guest logout dialog', async () => {
    const auth = useAuthStore()
    auth.setSession({
      access_token: 'guest-token',
      refresh_token: 'guest-refresh',
      token_type: 'bearer',
      user: { id: 1, username: 'guest_abc', name: '游客 abc', email: null, is_anonymous: true },
    }, true)

    const wrapper = mount(AppShell, {
      attachTo: document.body,
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true,
          ToastContainer: true,
        },
      },
    })

    await wrapper.findAll('button').find((button) => button.text().includes('退出登录'))!.trigger('click')

    expect(wrapper.get('[role="dialog"]').attributes('aria-modal')).toBe('true')
    expect(document.activeElement).toBe(wrapper.get('[data-testid="guest-register-action"]').element)
    wrapper.unmount()
  })
})
