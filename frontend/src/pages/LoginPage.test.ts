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
    expect(wrapper.text()).toContain('邮箱')
    expect(wrapper.text()).toContain('密码')
  })
})
