import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AssistantChatPanel from './AssistantChatPanel.vue'
import { useAssistantStore } from '@/stores/assistant'

describe('AssistantChatPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('sends the message when pressing Enter in the chat input', async () => {
    const assistant = useAssistantStore()
    assistant.loadConversation = vi.fn().mockResolvedValue(undefined)
    assistant.send = vi.fn()

    const wrapper = mount(AssistantChatPanel)
    const textarea = wrapper.get('textarea')

    await textarea.setValue('我下一步该怎么准备？')
    await textarea.trigger('keydown', { key: 'Enter' })

    expect(assistant.send).toHaveBeenCalledWith('我下一步该怎么准备？')
  })

  it('keeps the draft when pressing Enter while the assistant is responding', async () => {
    const assistant = useAssistantStore()
    assistant.isStreaming = true
    assistant.loadConversation = vi.fn().mockResolvedValue(undefined)
    assistant.send = vi.fn()

    const wrapper = mount(AssistantChatPanel)
    const textarea = wrapper.get('textarea')

    await textarea.setValue('先记下这个追问')
    await textarea.trigger('keydown', { key: 'Enter' })

    expect(assistant.send).not.toHaveBeenCalled()
    expect((textarea.element as HTMLTextAreaElement).value).toBe('先记下这个追问')
  })
})
