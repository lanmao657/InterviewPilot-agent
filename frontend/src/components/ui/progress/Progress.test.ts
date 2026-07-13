import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Progress from './Progress.vue'

describe('Progress accessibility', () => {
  it('exposes the clamped score to assistive technology', () => {
    const wrapper = mount(Progress, { props: { value: 120, label: '岗位匹配度' } })
    const progress = wrapper.get('[role="progressbar"]')

    expect(progress.attributes('aria-label')).toBe('岗位匹配度')
    expect(progress.attributes('aria-valuenow')).toBe('100')
  })
})
