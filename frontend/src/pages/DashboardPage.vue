<script setup lang="ts">
import { useMutation, useQuery } from '@tanstack/vue-query'
import {
  ArrowRight,
  Check,
  FileText,
  GitCompareArrows,
  Loader2,
  MessageSquareText,
  ShieldCheck,
  Target,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import JDKeywords, { type Keyword } from '@/components/JDKeywords.vue'
import JDMatchAnalysis from '@/components/JDMatchAnalysis.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const activePlan = computed(() => plansQuery.data.value?.[0])
const fitScore = computed(() => activePlan.value?.fit_score ?? 0)
const jdKeywords = computed(() => (activePlan.value?.roadmap as Record<string, unknown>)?.keywords as Keyword[] ?? [])
const hasResume = computed(() => documentsQuery.data.value?.some((item) => item.kind === 'resume') ?? false)
const hasJD = computed(() => documentsQuery.data.value?.some((item) => item.kind === 'job_description') ?? false)
const hasPlan = computed(() => Boolean(activePlan.value))
const hasQuestions = computed(() => (questionsQuery.data.value?.length ?? 0) > 0)
const hasReports = computed(() => (reportsQuery.data.value?.length ?? 0) > 0)

const journey = computed(() => [
  { label: '材料就绪', done: hasResume.value && hasJD.value },
  { label: '形成计划', done: hasPlan.value },
  { label: '针对训练', done: hasQuestions.value },
  { label: '完成复盘', done: hasReports.value },
])

const nextStep = computed(() => {
  if (!hasResume.value || !hasJD.value) {
    return {
      stage: '准备 · 第 1 步',
      title: '先建立可用的材料底稿',
      description: '上传一份简历和目标岗位描述，后续建议才会真正贴合你的经历。',
      action: '上传简历与岗位描述',
      path: '/documents',
    }
  }
  if (!hasPlan.value) {
    return {
      stage: '准备 · 第 2 步',
      title: '把岗位差距整理成准备路线',
      description: '材料已经齐全，接下来生成一份有优先级的准备计划。',
      action: '生成准备计划',
      path: '/documents',
    }
  }
  if (!hasQuestions.value) {
    return {
      stage: '训练 · 第 1 步',
      title: '把准备重点变成可练习的问题',
      description: '围绕岗位要求和简历证据，建立一组针对性题目。',
      action: '生成针对性题目',
      path: '/questions',
    }
  }
  if (!hasReports.value) {
    return {
      stage: '训练 · 第 2 步',
      title: '用一次完整回答检验准备成果',
      description: '完成一轮模拟面试，观察表达结构和证据是否足够清晰。',
      action: '开始模拟面试',
      path: '/interview',
    }
  }
  return {
    stage: '复盘 · 持续改进',
    title: '根据最近复盘继续收窄差距',
    description: '先处理报告里最弱的一项，再开始下一轮练习。',
    action: '查看最新复盘',
    path: '/reports',
  }
})

const showMatchAnalysis = ref(false)
const matchData = ref<{ matched: Array<{ requirement: string; evidence: string }>; gaps: Array<{ requirement: string; severity: string; suggestion: string }>; summary: string } | null>(null)
const matchMutation = useMutation({
  mutationFn: () => api.jdMatch(),
  onSuccess: (data) => {
    matchData.value = data
    showMatchAnalysis.value = true
  },
})
</script>

<template>
  <div class="flex flex-col gap-8">
    <section class="grid overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface)] lg:grid-cols-[1.35fr_0.65fr]">
      <div class="p-6 sm:p-8 lg:p-10">
        <p class="eyebrow mb-4">{{ nextStep.stage }}</p>
        <h2 class="max-w-2xl text-3xl font-semibold leading-tight sm:text-4xl">
          {{ nextStep.title }}
        </h2>
        <p class="mt-4 max-w-2xl text-base leading-7 text-[var(--text-secondary)]">
          {{ nextStep.description }}
        </p>
        <div class="mt-7 flex flex-wrap items-center gap-3">
          <Button data-testid="next-action" @click="router.push(nextStep.path)">
            {{ nextStep.action }}
            <ArrowRight class="size-4" />
          </Button>
          <Button v-if="activePlan" variant="ghost" @click="router.push(`/plans/${activePlan.id}`)">
            查看准备计划
          </Button>
        </div>
      </div>

      <aside class="border-t border-[var(--border)] bg-[var(--surface-muted)] p-6 lg:border-l lg:border-t-0 lg:p-8">
        <p class="text-xs font-bold tracking-[0.12em] text-[var(--text-muted)]">当前进度</p>
        <ol class="mt-5 space-y-4">
          <li v-for="(item, index) in journey" :key="item.label" class="flex items-center gap-3">
            <span
              class="grid size-7 shrink-0 place-items-center rounded-full border text-xs font-bold"
              :class="item.done
                ? 'border-[var(--success)] bg-[var(--success-light)] text-[var(--success)]'
                : 'border-[var(--border-strong)] bg-[var(--surface)] text-[var(--text-muted)]'"
            >
              <Check v-if="item.done" class="size-3.5" />
              <span v-else>{{ index + 1 }}</span>
            </span>
            <span :class="item.done ? 'text-[var(--text-secondary)]' : 'font-semibold'">{{ item.label }}</span>
          </li>
        </ol>
      </aside>
    </section>

    <section v-if="auth.isGuest" class="flex flex-col gap-4 rounded-[var(--radius-lg)] border border-[var(--primary)]/30 bg-[var(--primary)]/5 p-5 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex gap-3">
        <ShieldCheck class="mt-0.5 size-5 shrink-0 text-[var(--primary)]" />
        <div>
          <h2 class="text-base font-semibold">保存你的准备进度</h2>
          <p class="mt-1 text-sm text-[var(--text-secondary)]">注册后可长期保存材料、训练记录和复盘报告。</p>
        </div>
      </div>
      <Button variant="secondary" @click="router.push('/login?mode=register&guest=1')">注册正式账号</Button>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
      <div class="surface rounded-[var(--radius-lg)] p-6 sm:p-8">
        <div class="flex flex-col gap-4 border-b border-[var(--border)] pb-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p class="eyebrow">准备依据</p>
            <h2 class="mt-2 text-2xl font-semibold">{{ activePlan?.target_role ?? '目标岗位尚未建立' }}</h2>
            <p class="mt-2 text-sm text-[var(--text-secondary)]">
              {{ activePlan ? '围绕岗位要求，持续积累可以在面试中复述的证据。' : '材料齐全后，这里会展示岗位匹配结论与准备重点。' }}
            </p>
          </div>
          <Badge v-if="activePlan" variant="accent" class="self-start text-sm">匹配度 {{ fitScore }}</Badge>
        </div>

        <div v-if="activePlan" class="mt-6">
          <div class="mb-2 flex items-center justify-between text-xs text-[var(--text-muted)]">
            <span>岗位匹配度</span>
            <span class="font-mono tabular-nums">{{ fitScore }}/100</span>
          </div>
          <Progress :value="fitScore" />

          <div v-if="jdKeywords.length" class="mt-6">
            <p class="mb-3 text-sm font-semibold">高频岗位关键词</p>
            <JDKeywords :keywords="jdKeywords" />
          </div>

          <div class="mt-6 flex flex-wrap gap-2">
            <Button variant="secondary" :disabled="matchMutation.isPending.value" @click="matchMutation.mutate()">
              <Loader2 v-if="matchMutation.isPending.value" class="size-4 animate-spin" />
              <GitCompareArrows v-else class="size-4" />
              分析匹配差距
            </Button>
            <Button variant="ghost" @click="router.push(`/plans/${activePlan.id}`)">查看完整计划</Button>
          </div>

          <div v-if="showMatchAnalysis && matchData" class="mt-6 border-t border-[var(--border)] pt-6">
            <JDMatchAnalysis :data="matchData as any" />
          </div>
        </div>

        <div v-else class="mt-6 flex items-start gap-3 rounded-[var(--radius-md)] bg-[var(--surface-muted)] p-4">
          <FileText class="mt-0.5 size-5 shrink-0 text-[var(--primary)]" />
          <p class="text-sm leading-6 text-[var(--text-secondary)]">先上传简历与岗位描述，我们再把分散的信息整理成准备路线。</p>
        </div>
      </div>

      <aside class="surface rounded-[var(--radius-lg)] p-6">
        <p class="eyebrow">准备记录</p>
        <h2 class="mt-2 text-xl font-semibold">你的训练资产</h2>
        <dl class="mt-6 divide-y divide-[var(--border)] border-y border-[var(--border)]">
          <div class="flex items-center justify-between py-4">
            <dt class="flex items-center gap-2 text-sm text-[var(--text-secondary)]"><FileText class="size-4" />材料</dt>
            <dd class="font-mono text-lg font-semibold tabular-nums">{{ documentsQuery.data.value?.length ?? 0 }}</dd>
          </div>
          <div class="flex items-center justify-between py-4">
            <dt class="flex items-center gap-2 text-sm text-[var(--text-secondary)]"><Target class="size-4" />题目</dt>
            <dd class="font-mono text-lg font-semibold tabular-nums">{{ questionsQuery.data.value?.length ?? 0 }}</dd>
          </div>
          <div class="flex items-center justify-between py-4">
            <dt class="flex items-center gap-2 text-sm text-[var(--text-secondary)]"><MessageSquareText class="size-4" />复盘</dt>
            <dd class="font-mono text-lg font-semibold tabular-nums">{{ reportsQuery.data.value?.length ?? 0 }}</dd>
          </div>
        </dl>
      </aside>
    </section>
  </div>
</template>
