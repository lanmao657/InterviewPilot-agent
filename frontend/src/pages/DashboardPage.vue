<!-- frontend/src/pages/DashboardPage.vue -->
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowRight, BadgeCheck, BarChart3, BookOpenCheck, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

const router = useRouter()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const activePlan = computed(() => plansQuery.data.value?.[0])
const fitScore = computed(() => activePlan.value?.fit_score ?? 68)

const stats = computed(() => [
  { label: '准备计划', value: plansQuery.data.value?.length ?? 0, icon: FileText, color: 'var(--primary)' },
  { label: '资料', value: documentsQuery.data.value?.length ?? 0, icon: BookOpenCheck, color: 'var(--accent)' },
  { label: '题库', value: questionsQuery.data.value?.length ?? 0, icon: Target, color: 'var(--success)' },
  { label: '报告', value: reportsQuery.data.value?.length ?? 0, icon: BarChart3, color: 'var(--warning)' },
])
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 统计卡片 -->
    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="(stat, index) in stats"
        :key="stat.label"
        class="glass rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg animate-stagger"
        :style="{ '--stagger-index': index }"
      >
        <div class="mb-3 flex items-center justify-between">
          <component :is="stat.icon" class="size-5" :style="{ color: stat.color }" />
          <span class="text-3xl font-bold" :style="{ color: stat.color }">{{ stat.value }}</span>
        </div>
        <p class="text-sm text-[var(--text-secondary)]">{{ stat.label }}</p>
      </div>
    </section>

    <!-- 主要内容区 -->
    <section class="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
      <!-- 当前计划 -->
      <div class="glass-elevated rounded-2xl p-6">
        <div class="mb-5 flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold">当前准备计划</h2>
            <p class="text-sm text-[var(--text-secondary)]">{{ activePlan?.target_role ?? '上传简历与 JD 后生成专属路线' }}</p>
          </div>
          <Badge variant="accent" class="text-sm">Fit Score {{ fitScore }}</Badge>
        </div>

        <Progress :value="fitScore" class="mb-5" />

        <div class="mb-5 grid gap-3 sm:grid-cols-3">
          <div class="glass-flat rounded-xl p-4">
            <Target class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">岗位匹配</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">聚焦 JD 中最高频能力要求</p>
          </div>
          <div class="glass-flat rounded-xl p-4">
            <MessageSquareText class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">模拟追问</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">按回答动态生成追问题</p>
          </div>
          <div class="glass-flat rounded-xl p-4">
            <BadgeCheck class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">STAR Feedback</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">沉淀结构化复盘报告</p>
          </div>
        </div>

        <Button @click="router.push('/documents')">
          完善资料
          <ArrowRight class="size-4" />
        </Button>
      </div>

      <!-- 下一步行动 -->
      <div class="glass rounded-2xl p-6">
        <h2 class="mb-1 text-lg font-semibold">下一步行动</h2>
        <p class="mb-5 text-sm text-[var(--text-secondary)]">建议按顺序完成闭环</p>

        <div class="flex flex-col gap-3">
          <Button variant="secondary" class="justify-start" @click="router.push('/documents')">
            <FileText class="size-4" />
            上传简历与 JD
          </Button>
          <Button variant="secondary" class="justify-start" @click="router.push('/questions')">
            <Target class="size-4" />
            生成题库
          </Button>
          <Button class="justify-start" @click="router.push('/interview')">
            <MessageSquareText class="size-4" />
            开始模拟面试
          </Button>
        </div>
      </div>
    </section>
  </div>
</template>
