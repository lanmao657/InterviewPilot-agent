import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import LoginPage from './LoginPage.vue'

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

    await wrapper.find('button[type="button"]').trigger('click')

    expect(wrapper.text()).toContain('3-120 个字符，不能含 @')
    expect(wrapper.text()).toContain('至少 8 位')

    await wrapper.find('input[autocomplete="username"]').setValue('ab')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('用户名不合规范')
  })
})
