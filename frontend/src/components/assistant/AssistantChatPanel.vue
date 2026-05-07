<script setup lang="ts">
import { Send, Trash2 } from 'lucide-vue-next'
import { nextTick, onMounted, ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
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
  const message = input.value
  input.value = ''
  await assistant.send(message)
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
        <p class="text-sm font-semibold">AI 助手</p>
        <p class="text-xs text-muted-foreground">基于简历、JD、面试记录和报告回答</p>
      </div>
      <Button variant="ghost" size="icon" title="清空聊天" @click="assistant.clear">
        <Trash2 data-icon="inline-start" />
      </Button>
    </div>

    <div ref="scrollRef" class="min-h-0 flex-1 overflow-y-auto rounded-lg border bg-background/70 p-3">
      <div v-if="!assistant.messages.length" class="flex h-full min-h-44 flex-col justify-center gap-2 text-sm text-muted-foreground">
        <p class="font-medium text-foreground">可以这样问我：</p>
        <p>我下一步该怎么准备？</p>
        <p>帮我根据 JD 梳理 5 个高频追问。</p>
        <p>我的 STAR 回答哪里最需要加强？</p>
      </div>
      <div v-else class="flex flex-col gap-3">
        <div
          v-for="message in assistant.messages"
          :key="message.id"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[88%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm leading-6"
            :class="message.role === 'user' ? 'bg-primary text-primary-foreground' : 'border bg-card text-card-foreground'"
          >
            {{ message.content || (message.status === 'streaming' ? '正在生成...' : '') }}
          </div>
        </div>
      </div>
    </div>

    <p v-if="assistant.error" class="text-xs text-destructive">{{ assistant.error }}</p>
    <form class="flex gap-2" @submit.prevent="send">
      <Textarea
        v-model="input"
        :class="compact ? 'min-h-16' : 'min-h-20'"
        placeholder="问问 AI 助手，比如：我下一步该怎么准备？"
        @keydown.ctrl.enter.prevent="send"
      />
      <Button type="submit" size="icon" :disabled="assistant.isStreaming || !input.trim()">
        <Send data-icon="inline-start" />
      </Button>
    </form>
  </div>
</template>
