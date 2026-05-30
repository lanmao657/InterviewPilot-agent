<!-- frontend/src/pages/InterviewPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { Bot, RotateCcw, Send, Sparkles, Timer } from 'lucide-vue-next'
import { computed, onBeforeUnmount, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { api, streamApi, type Interview, type Question } from '@/lib/api'

const queryClient = useQueryClient()
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const interview = ref<Interview | null>(null)
const selectedQuestion = ref('')
const selectedQuestionId = ref<number | null>(null)
const answer = ref('')
const followUp = ref('')
const streaming = ref(false)
const showQuestionBank = ref(true)

// 面试模式：practice（练习）/ real（真实）
type InterviewMode = 'practice' | 'real'
const mode = ref<InterviewMode>('practice')
const timerDurationOptions = [
  { label: '3 分钟', value: 180 },
  { label: '5 分钟', value: 300 },
  { label: '8 分钟', value: 480 },
]

// 计时器相关
const timerDuration = ref(300) // 默认 5 分钟（秒）
const timerRemaining = ref(0)
const timerRunning = ref(false)
const timerExpired = ref(false)
let timerInterval: ReturnType<typeof setInterval> | null = null
const totalTimeUsed = ref(0) // 面试总用时（秒）
let interviewStartTime = 0

const latestTurn = computed(() => interview.value?.turns.at(-1))
const score = computed(() => interview.value?.current_score ?? 0)
const answeredCount = computed(() => interview.value?.turns.length ?? 0)
const totalQuestions = computed(() => questionsQuery.data.value?.length ?? 0)
const answerWordCount = computed(() => answer.value.trim() ? answer.value.trim().length : 0)

// 格式化时间显示（秒 → mm:ss）
function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

// 启动计时器
function startTimer() {
  stopTimer()
  timerRemaining.value = timerDuration.value
  timerExpired.value = false
  timerRunning.value = true
  timerInterval = setInterval(() => {
    timerRemaining.value--
    if (timerRemaining.value <= 0) {
      timerExpired.value = true
      stopTimer()
    }
  }, 1000)
}

// 停止计时器
function stopTimer() {
  timerRunning.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 计时器颜色：剩余时间不足 60 秒时变红
const timerColor = computed(() => {
  if (timerExpired.value) return 'var(--error)'
  if (timerRemaining.value <= 60) return 'var(--warning)'
  return 'var(--primary)'
})

const createMutation = useMutation({
  mutationFn: () => api.createInterview({ prep_plan_id: plansQuery.data.value?.[0]?.id, title: '文字模拟面试' }),
  onSuccess: (data) => {
    interview.value = data
    interviewStartTime = Date.now()
  },
})

const answerMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    return api.answer(interview.value.id, { question: selectedQuestion.value, answer: answer.value })
  },
  onSuccess: async (data) => {
    interview.value = data
    stopTimer()
    answer.value = ''
    await streamFollowUp()
    // 自动启动下一题计时
    startTimer()
  },
})

const reportMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    // 记录总用时
    if (interviewStartTime) {
      totalTimeUsed.value = Math.floor((Date.now() - interviewStartTime) / 1000)
    }
    return api.createReport(interview.value.id)
  },
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reports'] }),
})

function selectQuestion(question: Question) {
  selectedQuestionId.value = question.id
  selectedQuestion.value = question.prompt
  // 切换题目时重启计时器
  if (interview.value) startTimer()
}

async function startInterview() {
  await createMutation.mutateAsync()
  if (!selectedQuestion.value && questionsQuery.data.value?.length) {
    selectQuestion(questionsQuery.data.value[0])
  }
  startTimer()
}

async function streamFollowUp() {
  if (!interview.value) return
  followUp.value = ''
  streaming.value = true
  try {
    await streamApi(`/stream/interviews/${interview.value.id}/follow-up`, (chunk) => {
      followUp.value += chunk
    })
  } finally {
    streaming.value = false
  }
}

function useFollowUp() {
  if (followUp.value) {
    selectedQuestion.value = followUp.value
    selectedQuestionId.value = null
  }
}

const difficultyLabel: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
const difficultyVariant: Record<string, 'default' | 'accent' | 'warning'> = {
  easy: 'default',
  medium: 'accent',
  hard: 'warning',
}

// 组件销毁时清理计时器
onBeforeUnmount(() => stopTimer())
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[1fr_360px]">
    <!-- 主面试区 -->
    <div class="glass rounded-2xl p-6">
      <div class="mb-5 flex items-start justify-between">
        <div>
          <h2 class="text-lg font-semibold">模拟面试</h2>
          <p class="text-sm text-[var(--text-secondary)]">
            {{ mode === 'real' ? '真实模式：隐藏实时评分，模拟真实面试压力' : '练习模式：即时反馈，适合日常训练' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <!-- 模式切换（面试开始前显示） -->
          <div v-if="!interview" class="flex rounded-lg bg-[var(--bg-input)] p-0.5">
            <button
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-all"
              :class="mode === 'practice' ? 'bg-[var(--primary)] text-white shadow-sm' : 'text-[var(--text-muted)]'"
              @click="mode = 'practice'"
            >
              练习模式
            </button>
            <button
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-all"
              :class="mode === 'real' ? 'bg-[var(--primary)] text-white shadow-sm' : 'text-[var(--text-muted)]'"
              @click="mode = 'real'"
            >
              真实模式
            </button>
          </div>
          <!-- 真实模式计时配置 -->
          <select
            v-if="mode === 'real' && !interview"
            v-model="timerDuration"
            class="rounded-lg bg-[var(--bg-input)] px-2 py-1 text-xs border border-[var(--border)]"
          >
            <option v-for="opt in timerDurationOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <!-- 计时器 -->
          <div
            v-if="interview && timerRunning"
            class="flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-mono font-semibold"
            :style="{ color: timerColor, background: `${timerColor}15`, border: `1px solid ${timerColor}30` }"
          >
            <Timer class="size-3.5" />
            {{ formatTime(timerRemaining) }}
          </div>
          <div
            v-else-if="timerExpired"
            class="flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold text-[var(--error)] bg-[var(--error)]/10 border border-[var(--error)]/30"
          >
            <Timer class="size-3.5" />
            时间到
          </div>
          <!-- 总用时 -->
          <div
            v-if="totalTimeUsed > 0"
            class="text-xs text-[var(--text-muted)]"
          >
            总用时 {{ formatTime(totalTimeUsed) }}
          </div>
          <Badge v-if="mode !== 'real' && answeredCount > 0" variant="default" class="text-xs">
            已答 {{ answeredCount }}{{ totalQuestions ? `/${totalQuestions}` : '' }} 题
          </Badge>
          <Badge v-if="mode !== 'real'" variant="accent" class="text-sm">当前得分 {{ score || '--' }}</Badge>
        </div>
      </div>

      <!-- 进度条 -->
      <Progress v-if="totalQuestions > 0" :value="(answeredCount / totalQuestions) * 100" class="mb-5" />

      <div class="flex flex-col gap-5">
        <!-- 面试官问题 -->
        <div class="glass-elevated rounded-xl p-5">
          <div class="mb-2 flex items-center gap-2 text-sm font-semibold">
            <Bot class="size-4 text-[var(--primary)]" />
            面试官问题
            <span v-if="selectedQuestionId" class="text-xs font-normal text-[var(--text-muted)]">
              来自题库
            </span>
            <span v-else-if="followUp" class="text-xs font-normal text-[var(--text-muted)]">
              来自追问
            </span>
          </div>
          <p class="text-base leading-7">{{ selectedQuestion || '请从右侧题库选择一道题目，或点击"开始面试"自动选择。' }}</p>
        </div>

        <!-- 回答输入 -->
        <div>
          <Textarea v-model="answer" class="min-h-44" placeholder="输入你的回答，尽量使用 STAR 结构并补充量化结果。" />
          <p class="mt-1 text-right text-xs text-[var(--text-muted)]">{{ answerWordCount }} 字</p>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-wrap gap-3">
          <Button :disabled="createMutation.isPending.value" @click="startInterview">
            <Sparkles class="size-4" />
            {{ interview ? '重新开始' : '开始面试' }}
          </Button>
          <Button
            :disabled="!interview || !answer.trim() || answerMutation.isPending.value"
            @click="answerMutation.mutate()"
          >
            <Send class="size-4" />
            提交回答
          </Button>
          <Button
            v-if="interview && answeredCount > 0"
            variant="secondary"
            :disabled="reportMutation.isPending.value"
            @click="reportMutation.mutate()"
          >
            生成报告
          </Button>
        </div>
      </div>
    </div>

    <!-- 侧边栏 -->
    <aside class="flex flex-col gap-5">
      <!-- 题库选择 -->
      <div class="glass rounded-2xl p-5">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-base font-semibold">题库</h3>
          <Button variant="ghost" size="sm" @click="showQuestionBank = !showQuestionBank">
            {{ showQuestionBank ? '收起' : '展开' }}
          </Button>
        </div>
        <div v-if="showQuestionBank" class="flex max-h-60 flex-col gap-2 overflow-y-auto">
          <button
            v-for="question in questionsQuery.data.value"
            :key="question.id"
            class="rounded-lg p-3 text-left text-sm transition-all"
            :class="selectedQuestionId === question.id
              ? 'glass-elevated ring-1 ring-[var(--primary)]'
              : 'glass-flat hover:bg-[var(--glass-bg-hover)]'"
            @click="selectQuestion(question)"
          >
            <div class="mb-1 flex items-center gap-2">
              <Badge :variant="difficultyVariant[question.difficulty] ?? 'default'" class="text-[10px]">
                {{ difficultyLabel[question.difficulty] ?? question.difficulty }}
              </Badge>
              <span class="text-[11px] text-[var(--text-muted)]">{{ question.category }}</span>
            </div>
            <p class="line-clamp-2 leading-5 text-[var(--text-secondary)]">{{ question.prompt }}</p>
          </button>
          <p v-if="!questionsQuery.data.value?.length" class="text-sm text-[var(--text-muted)]">
            还没有题目，请先在题库页生成。
          </p>
        </div>
      </div>

      <!-- 追问（练习模式显示） -->
      <div v-if="mode === 'practice'" class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">追问</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">
          {{ streaming ? 'AI 正在生成...' : followUp ? '根据上一轮回答动态生成' : '提交回答后自动生成追问' }}
        </p>
        <p v-if="followUp" class="text-sm leading-6 text-[var(--text-secondary)]">{{ followUp }}</p>
        <Button v-if="followUp && !streaming" variant="ghost" size="sm" class="mt-2" @click="useFollowUp">
          <RotateCcw class="size-3" />
          使用此追问
        </Button>
      </div>

      <!-- 评分摘要（练习模式显示） -->
      <div v-if="mode === 'practice'" class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">评分摘要</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">即时反馈会沉淀到报告</p>
        <Progress :value="score" class="mb-3" />
        <p class="text-sm text-[var(--text-secondary)]">
          {{ latestTurn?.feedback?.summary ?? '提交第一段回答后查看 STAR Feedback。' }}
        </p>
      </div>

      <!-- 真实模式：面试结束后显示完整回顾 -->
      <div v-if="mode === 'real' && totalTimeUsed > 0" class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">面试回顾</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">面试已结束，以下是你的表现总结</p>
        <div class="mb-3 flex items-center gap-3">
          <span class="text-3xl font-bold text-[var(--primary)]">{{ score }}</span>
          <span class="text-sm text-[var(--text-muted)]">综合得分</span>
        </div>
        <p class="text-xs text-[var(--text-muted)]">
          总用时 {{ Math.floor(totalTimeUsed / 60) }} 分 {{ totalTimeUsed % 60 }} 秒 ·
          共回答 {{ answeredCount }} 题 ·
          平均每题 {{ answeredCount > 0 ? Math.round(totalTimeUsed / answeredCount) : 0 }} 秒
        </p>
      </div>

      <!-- 最近问答 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-3 text-base font-semibold">最近问答</h3>
        <div class="flex max-h-48 flex-col gap-3 overflow-y-auto">
          <div v-for="turn in interview?.turns" :key="turn.id" class="glass-flat rounded-lg p-3">
            <p class="text-sm font-medium">{{ turn.question }}</p>
            <p v-if="mode === 'practice' || totalTimeUsed > 0" class="mt-1 text-xs text-[var(--text-muted)]">得分 {{ turn.score }}</p>
            <p v-else class="mt-1 text-xs text-[var(--text-muted)]">已回答</p>
          </div>
          <p v-if="!interview?.turns.length" class="text-sm text-[var(--text-muted)]">还没有提交回答。</p>
        </div>
      </div>
    </aside>
  </div>
</template>
