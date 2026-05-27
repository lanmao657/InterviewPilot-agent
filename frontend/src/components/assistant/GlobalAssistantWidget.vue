<script setup lang="ts">
import { Bot, X } from 'lucide-vue-next'
import { ref } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Button } from '@/components/ui/button'

const open = ref(false)
</script>

<template>
  <div class="fixed bottom-20 right-4 z-40 flex flex-col items-end gap-3 lg:bottom-5">
    <Transition name="scale">
      <div v-if="open" class="glass-elevated h-[min(620px,calc(100vh-7rem))] w-[min(420px,calc(100vw-2rem))] rounded-2xl p-4">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <div class="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-white">
              <Bot class="size-4" />
            </div>
            <div>
              <p class="text-sm font-semibold">InterviewPilot AI 助手</p>
              <p class="text-xs text-[var(--text-muted)]">全局流式问答</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" @click="open = false">
            <X class="size-4" />
          </Button>
        </div>
        <AssistantChatPanel compact />
      </div>
    </Transition>

    <Button size="lg" class="h-12 rounded-full px-5 shadow-lg" @click="open = !open">
      <Bot class="size-5" />
      AI 助手
    </Button>
  </div>
</template>

<style scoped>
.scale-enter-active {
  animation: scale-in 200ms ease-out;
}
.scale-leave-active {
  animation: scale-out 150ms ease-in;
}
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.9) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes scale-out {
  from { opacity: 1; transform: scale(1) translateY(0); }
  to { opacity: 0; transform: scale(0.9) translateY(10px); }
}
</style>
