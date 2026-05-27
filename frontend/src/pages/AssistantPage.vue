<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Bot, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'

const contextQuery = useQuery({ queryKey: ['assistant-context'], queryFn: api.assistantContext })

const documents = computed(() => contextQuery.data.value?.documents ?? [])
const activePlan = computed(() => contextQuery.data.value?.activePlan)
const recentInterview = computed(() => contextQuery.data.value?.recentInterview)
const latestReport = computed(() => contextQuery.data.value?.latestReport)
</script>

<template>
  <div class="grid min-h-[calc(100vh-12rem)] gap-5 xl:grid-cols-[1fr_360px]">
    <div class="glass rounded-2xl p-5">
      <AssistantChatPanel />
    </div>

    <aside class="flex flex-col gap-4">
      <div class="glass rounded-2xl p-5">
        <div class="mb-4 flex items-center gap-2">
          <Bot class="size-5 text-[var(--primary)]" />
          <h3 class="font-semibold">引用上下文</h3>
        </div>
        <p class="mb-4 text-xs text-[var(--text-muted)]">助手会优先参考这些本地资料</p>

        <div class="flex flex-col gap-3">
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-medium">准备计划</span>
              <Badge variant="accent">{{ activePlan ? '已生成' : '未生成' }}</Badge>
            </div>
            <p class="mt-2 text-xs text-[var(--text-muted)]">{{ activePlan?.title ?? '上传简历与 JD 后生成计划' }}</p>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <FileText class="size-4 text-[var(--primary)]" />
              资料 {{ documents.length }}
            </div>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <Target class="size-4 text-[var(--primary)]" />
              题库 {{ contextQuery.data.value?.questionCount ?? 0 }}
            </div>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <MessageSquareText class="size-4 text-[var(--primary)]" />
              最近面试
            </div>
            <p class="mt-1 text-xs text-[var(--text-muted)]">
              {{ recentInterview ? `最近得分 ${recentInterview.currentScore ?? 0}` : '还没有模拟面试记录' }}
            </p>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <p class="text-sm font-medium">最新报告</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">{{ latestReport ? latestReport.title : '生成报告后，助手会引用复盘结论' }}</p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>
