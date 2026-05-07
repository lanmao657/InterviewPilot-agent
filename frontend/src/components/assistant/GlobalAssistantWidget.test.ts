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

    expect(wrapper.text()).toContain('AI 助手')
    await wrapper.get('button').trigger('click')

    expect(wrapper.text()).toContain('InterviewPilot AI 助手')
    expect(wrapper.text()).toContain('基于简历、JD、面试记录和报告回答')
  })
})
