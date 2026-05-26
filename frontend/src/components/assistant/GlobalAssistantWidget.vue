<script setup lang="ts">
import { Bot, X } from 'lucide-vue-next'
import { ref } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

const open = ref(false)
</script>

<template>
  <div class="fixed bottom-5 right-5 z-30 flex flex-col items-end gap-3">
    <Card v-if="open" class="h-[min(620px,calc(100vh-7rem))] w-[min(420px,calc(100vw-2rem))] p-4 shadow-xl">
      <div class="mb-3 flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <div class="grid size-9 place-items-center rounded-md bg-primary text-primary-foreground">
            <Bot data-icon="inline-start" />
          </div>
          <div>
            <p class="text-sm font-semibold">InterviewPilot AI 助手</p>
            <p class="text-xs text-muted-foreground">全局流式问答</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" @click="open = false">
          <X data-icon="inline-start" />
        </Button>
      </div>
      <AssistantChatPanel compact />
    </Card>

    <Button size="lg" class="h-12 rounded-full px-5 shadow-lg" @click="open = !open">
      <Bot data-icon="inline-start" />
      AI 助手
    </Button>
  </div>
</template>
