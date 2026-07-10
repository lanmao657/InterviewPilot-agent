<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { FileText, MessageCircleQuestion, MessageSquareText, Target } from 'lucide-vue-next'
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
  <div class="grid min-h-[calc(100dvh-11rem)] items-start gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
    <section class="surface-raised min-h-[650px] rounded-[var(--radius-lg)] p-5 sm:p-7">
      <AssistantChatPanel />
    </section>

    <aside class="surface rounded-[var(--radius-lg)] p-5 xl:sticky xl:top-28">
        <div class="mb-4 flex items-center gap-2">
          <MessageCircleQuestion class="size-5 text-[var(--primary)]" />
          <h2 class="text-lg font-semibold">本次建议参考</h2>
        </div>
        <p class="mb-5 text-sm leading-6 text-[var(--text-secondary)]">回答会优先结合以下资料；缺少的内容不会被假定为已知。</p>

        <div class="divide-y divide-[var(--border)] border-y border-[var(--border)]">
          <div class="py-4">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-medium">准备计划</span>
              <Badge variant="accent">{{ activePlan ? '已生成' : '未生成' }}</Badge>
            </div>
            <p class="mt-2 text-xs text-[var(--text-muted)]">{{ activePlan?.title ?? '上传简历与 JD 后生成计划' }}</p>
          </div>
          <div class="py-4">
            <div class="flex items-center gap-2 text-sm font-medium">
              <FileText class="size-4 text-[var(--primary)]" />
              资料 {{ documents.length }}
            </div>
          </div>
          <div class="py-4">
            <div class="flex items-center gap-2 text-sm font-medium">
              <Target class="size-4 text-[var(--primary)]" />
              题库 {{ contextQuery.data.value?.questionCount ?? 0 }}
            </div>
          </div>
          <div class="py-4">
            <div class="flex items-center gap-2 text-sm font-medium">
              <MessageSquareText class="size-4 text-[var(--primary)]" />
              最近面试
            </div>
            <p class="mt-1 text-xs text-[var(--text-muted)]">
              {{ recentInterview ? `最近得分 ${recentInterview.currentScore ?? 0}` : '还没有模拟面试记录' }}
            </p>
          </div>
          <div class="py-4">
            <p class="text-sm font-medium">最新报告</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">{{ latestReport ? latestReport.title : '生成报告后，助手会引用复盘结论' }}</p>
          </div>
        </div>
    </aside>
  </div>
</template>
