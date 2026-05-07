<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Bot, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'

const contextQuery = useQuery({ queryKey: ['assistant-context'], queryFn: api.assistantContext })

const documents = computed(() => contextQuery.data.value?.documents ?? [])
const activePlan = computed(() => contextQuery.data.value?.activePlan)
const recentInterview = computed(() => contextQuery.data.value?.recentInterview)
const latestReport = computed(() => contextQuery.data.value?.latestReport)
</script>

<template>
  <div class="grid min-h-[calc(100vh-8rem)] gap-5 xl:grid-cols-[1fr_360px]">
    <Card class="min-h-0 p-5">
      <AssistantChatPanel />
    </Card>

    <aside class="flex flex-col gap-5">
      <Card>
        <CardHeader>
          <div class="flex items-center gap-2">
            <Bot class="text-primary" />
            <CardTitle>引用上下文</CardTitle>
          </div>
          <CardDescription>助手会优先参考这些本地资料。</CardDescription>
        </CardHeader>
        <CardContent class="flex flex-col gap-3">
          <div class="rounded-lg border bg-background/70 p-3">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-medium">准备计划</span>
              <Badge variant="accent">{{ activePlan ? '已生成' : '未生成' }}</Badge>
            </div>
            <p class="mt-2 text-sm text-muted-foreground">
              {{ activePlan?.title ?? '上传简历与 JD 后生成计划，助手会给出更具体建议。' }}
            </p>
          </div>

          <div class="rounded-lg border bg-background/70 p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <FileText class="text-primary" />
              资料 {{ documents.length }}
            </div>
            <p class="mt-2 text-sm text-muted-foreground">
              {{ documents.length ? '已读取最近上传的简历与 JD 摘要。' : '还没有资料。' }}
            </p>
          </div>

          <div class="rounded-lg border bg-background/70 p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <Target class="text-primary" />
              题库 {{ contextQuery.data.value?.questionCount ?? 0 }}
            </div>
            <p class="mt-2 text-sm text-muted-foreground">助手会结合题库数量建议训练节奏。</p>
          </div>

          <div class="rounded-lg border bg-background/70 p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <MessageSquareText class="text-primary" />
              最近面试
            </div>
            <p class="mt-2 text-sm text-muted-foreground">
              {{ recentInterview ? `最近得分 ${recentInterview.currentScore ?? 0}` : '还没有模拟面试记录。' }}
            </p>
          </div>

          <div class="rounded-lg border bg-background/70 p-3">
            <p class="text-sm font-medium">最新报告</p>
            <p class="mt-2 text-sm text-muted-foreground">
              {{ latestReport ? latestReport.title : '生成报告后，助手会引用复盘结论。' }}
            </p>
          </div>
        </CardContent>
      </Card>
    </aside>
  </div>
</template>
