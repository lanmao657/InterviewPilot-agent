<!-- frontend/src/pages/InterviewPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { Bot, Send, Sparkles } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { api, streamApi, type Interview } from '@/lib/api'

const queryClient = useQueryClient()
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const interview = ref<Interview | null>(null)
const selectedQuestion = ref('请介绍一个最能体现你岗位匹配度的项目。')
const answer = ref('')
const followUp = ref('')
const streaming = ref(false)

const latestTurn = computed(() => interview.value?.turns.at(-1))
const score = computed(() => interview.value?.current_score ?? 0)

const createMutation = useMutation({
  mutationFn: () => api.createInterview({ prep_plan_id: plansQuery.data.value?.[0]?.id, title: '文字模拟面试' }),
  onSuccess: (data) => { interview.value = data },
})

const answerMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    return api.answer(interview.value.id, { question: selectedQuestion.value, answer: answer.value })
  },
  onSuccess: async (data) => {
    interview.value = data
    answer.value = ''
    await streamFollowUp()
  },
})

const reportMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    return api.createReport(interview.value.id)
  },
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reports'] }),
})

async function startInterview() {
  await createMutation.mutateAsync()
  selectedQuestion.value = questionsQuery.data.value?.[0]?.prompt ?? selectedQuestion.value
}

async function streamFollowUp() {
  if (!interview.value) return
  followUp.value = ''
  streaming.value = true
  try {
    await streamApi(`/stream/interviews/${interview.value.id}/follow-up`, (chunk) => {
      followUp.value += chunk
    })
    if (followUp.value) selectedQuestion.value = followUp.value
  } finally {
    streaming.value = false
  }
}
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[1fr_360px]">
    <!-- 主面试区 -->
    <div class="glass rounded-2xl p-6">
      <div class="mb-5 flex items-start justify-between">
        <div>
          <h2 class="text-lg font-semibold">模拟面试</h2>
          <p class="text-sm text-[var(--text-secondary)]">文字问答优先，AI 会根据回答生成追问</p>
        </div>
        <Badge variant="accent" class="text-sm">当前得分 {{ score || '--' }}</Badge>
      </div>

      <div class="flex flex-col gap-5">
        <!-- 面试官问题 -->
        <div class="glass-elevated rounded-xl p-5">
          <div class="mb-2 flex items-center gap-2 text-sm font-semibold">
            <Bot class="size-4 text-[var(--primary)]" />
            面试官问题
          </div>
          <p class="text-base leading-7">{{ selectedQuestion }}</p>
        </div>

        <!-- 回答输入 -->
        <Textarea v-model="answer" class="min-h-44" placeholder="输入你的回答，尽量使用 STAR 结构并补充量化结果。" />

        <!-- 操作按钮 -->
        <div class="flex flex-wrap gap-3">
          <Button :disabled="createMutation.isPending.value" @click="startInterview">
            <Sparkles class="size-4" />
            {{ interview ? '重新开始' : '开始面试' }}
          </Button>
          <Button :disabled="!interview || !answer || answerMutation.isPending.value" @click="answerMutation.mutate()">
            <Send class="size-4" />
            提交回答
          </Button>
          <Button variant="secondary" :disabled="!interview || reportMutation.isPending.value" @click="reportMutation.mutate()">
            生成报告
          </Button>
        </div>
      </div>
    </div>

    <!-- 侧边栏 -->
    <aside class="flex flex-col gap-5">
      <!-- 评分摘要 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">评分摘要</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">即时反馈会沉淀到报告</p>
        <Progress :value="score" class="mb-3" />
        <p class="text-sm text-[var(--text-secondary)]">
          {{ latestTurn?.feedback?.summary ?? '提交第一段回答后查看 STAR Feedback。' }}
        </p>
      </div>

      <!-- 追问 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">追问</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">{{ streaming ? 'AI 正在生成...' : '根据上一轮回答动态生成' }}</p>
        <p class="text-sm leading-6 text-[var(--text-secondary)]">{{ followUp || '暂无追问。' }}</p>
      </div>

      <!-- 最近问答 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-3 text-base font-semibold">最近问答</h3>
        <div class="flex flex-col gap-3">
          <div v-for="turn in interview?.turns" :key="turn.id" class="glass-flat rounded-lg p-3">
            <p class="text-sm font-medium">{{ turn.question }}</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">得分 {{ turn.score }}</p>
          </div>
          <p v-if="!interview?.turns.length" class="text-sm text-[var(--text-muted)]">还没有提交回答。</p>
        </div>
      </div>
    </aside>
  </div>
</template>
