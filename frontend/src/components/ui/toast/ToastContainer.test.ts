import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useToastStore } from '@/stores/toast'
import ToastContainer from './ToastContainer.vue'

describe('ToastContainer accessibility', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('announces notifications without stealing focus', () => {
    useToastStore().show('资料已保存', 'success')
    const wrapper = mount(ToastContainer)

    const region = wrapper.get('[aria-live="polite"]')
    expect(region.attributes('aria-atomic')).toBe('false')
    expect(region.text()).toContain('资料已保存')
    expect(wrapper.get('button').attributes('aria-label')).toBe('关闭通知')
  })
})
