import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import GlobalAssistantWidget from './GlobalAssistantWidget.vue'

describe('GlobalAssistantWidget', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('opens the assistant chat panel', async () => {
    const wrapper = mount(GlobalAssistantWidget)

    expect(wrapper.text()).toContain('问教练')
    await wrapper.get('button').trigger('click')

    expect(wrapper.text()).toContain('教练对话')
    expect(wrapper.text()).toContain('结合你的材料与训练记录给出建议')
  })
})
