<script setup lang="ts">
import { Send, Trash2 } from 'lucide-vue-next'
import { nextTick, onMounted, ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { renderMarkdown } from '@/lib/markdown'
import { useAssistantStore } from '@/stores/assistant'

const props = withDefaults(defineProps<{ compact?: boolean }>(), {
  compact: false,
})

const assistant = useAssistantStore()
const input = ref('')
const scrollRef = ref<HTMLElement | null>(null)

onMounted(() => {
  assistant.loadConversation().catch(() => undefined)
})

async function send() {
  const message = input.value.trim()
  if (!message || assistant.isStreaming) return
  input.value = ''
  await assistant.send(message)
}

function handleInputKeydown(event: KeyboardEvent) {
  if (event.key !== 'Enter' || event.shiftKey || event.isComposing) return
  event.preventDefault()
  send()
}

watch(
  () => assistant.messages.map((item) => item.content).join(''),
  async () => {
    await nextTick()
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  },
)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col gap-3">
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="font-display text-lg font-semibold">教练对话</p>
        <p class="text-xs text-[var(--text-muted)]">结合你的材料与训练记录给出建议</p>
      </div>
      <Button variant="ghost" size="icon" title="清空聊天" @click="assistant.clear">
        <Trash2 class="size-4" />
      </Button>
    </div>

    <div ref="scrollRef" class="min-h-0 flex-1 overflow-y-auto border-y border-[var(--border)] py-4">
      <div v-if="!assistant.messages.length" class="flex h-full min-h-44 flex-col justify-center gap-2 text-sm text-[var(--text-muted)]">
        <p class="font-medium text-[var(--text-primary)]">可以从当前任务开始：</p>
        <p>根据现有材料，我下一步最应该补什么？</p>
        <p>帮我围绕岗位要求梳理 5 个高频追问。</p>
        <p>最近一次回答里，哪部分证据最薄弱？</p>
      </div>
      <div v-else class="flex flex-col gap-3">
        <div
          v-for="message in assistant.messages"
          :key="message.id"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[88%] whitespace-pre-wrap rounded-xl px-4 py-2.5 text-sm leading-6"
            :class="message.role === 'user'
              ? 'bg-[var(--primary)] text-[var(--text-on-primary)]'
              : 'border border-[var(--border)] bg-[var(--surface-muted)] markdown-body'"
            v-if="message.role === 'user'"
          >
            {{ message.content }}
          </div>
          <div
            v-else
            class="markdown-body max-w-[88%] rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-2.5 text-sm leading-6"
            v-html="message.content ? renderMarkdown(message.content) : (message.status === 'streaming' ? '<em>正在生成...</em>' : '')"
          />
        </div>
      </div>
    </div>

    <p v-if="assistant.error" class="text-xs text-[var(--error)]">{{ assistant.error }}</p>
    <form class="flex gap-2" @submit.prevent="send">
      <Textarea
        v-model="input"
        :class="compact ? 'min-h-16' : 'min-h-20'"
        placeholder="描述你正在准备的问题…"
        @keydown="handleInputKeydown"
      />
      <Button type="submit" size="icon" :disabled="assistant.isStreaming || !input.trim()">
        <Send class="size-4" />
      </Button>
    </form>
  </div>
</template>
