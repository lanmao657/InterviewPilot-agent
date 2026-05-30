<!-- frontend/src/components/ResumeAnalysis.vue -->
<!-- 简历诊断评分组件 -->
<script setup lang="ts">
import { AlertCircle, CheckCircle, Lightbulb } from 'lucide-vue-next'
import { computed } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface AnalysisModule {
  name: string
  score: number
  comment: string
}

interface AnalysisData {
  overall_score: number
  modules: AnalysisModule[]
  issues: string[]
  suggestions: string[]
}

const props = defineProps<{ data: AnalysisData }>()

// 根据分数返回颜色
function scoreColor(score: number): string {
  if (score >= 80) return 'var(--success)'
  if (score >= 60) return 'var(--warning)'
  return 'var(--error)'
}

// 根据分数返回等级文字
function scoreLevel(score: number): string {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '需改进'
}

const sortedModules = computed(() =>
  [...(props.data.modules ?? [])].sort((a, b) => a.score - b.score)
)
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- 总分展示 -->
    <div class="flex items-center gap-4">
      <div
        class="grid size-20 place-items-center rounded-full border-4 text-2xl font-bold"
        :style="{ borderColor: scoreColor(data.overall_score), color: scoreColor(data.overall_score) }"
      >
        {{ data.overall_score }}
      </div>
      <div>
        <p class="text-lg font-semibold">简历质量评分</p>
        <Badge :variant="data.overall_score >= 70 ? 'accent' : 'warning'" class="mt-1">
          {{ scoreLevel(data.overall_score) }}
        </Badge>
      </div>
    </div>

    <!-- 各模块得分 -->
    <div class="flex flex-col gap-3">
      <p class="text-sm font-semibold text-[var(--text-secondary)]">各模块评分</p>
      <div v-for="mod in sortedModules" :key="mod.name" class="flex flex-col gap-1.5">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium">{{ mod.name }}</span>
          <span class="font-semibold" :style="{ color: scoreColor(mod.score) }">{{ mod.score }} 分</span>
        </div>
        <Progress :value="mod.score" class="h-2" />
        <p class="text-xs text-[var(--text-muted)]">{{ mod.comment }}</p>
      </div>
    </div>

    <!-- 问题列表 -->
    <div v-if="data.issues?.length" class="flex flex-col gap-2">
      <p class="flex items-center gap-1.5 text-sm font-semibold text-[var(--text-secondary)]">
        <AlertCircle class="size-4 text-[var(--warning)]" />
        发现的问题
      </p>
      <ul class="flex flex-col gap-1.5">
        <li v-for="(issue, i) in data.issues" :key="i" class="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
          <span class="mt-1 size-1.5 shrink-0 rounded-full bg-[var(--warning)]" />
          {{ issue }}
        </li>
      </ul>
    </div>

    <!-- 改进建议 -->
    <div v-if="data.suggestions?.length" class="flex flex-col gap-2">
      <p class="flex items-center gap-1.5 text-sm font-semibold text-[var(--text-secondary)]">
        <Lightbulb class="size-4 text-[var(--primary)]" />
        改进建议
      </p>
      <ul class="flex flex-col gap-1.5">
        <li v-for="(suggestion, i) in data.suggestions" :key="i" class="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
          <CheckCircle class="mt-0.5 size-3.5 shrink-0 text-[var(--success)]" />
          {{ suggestion }}
        </li>
      </ul>
    </div>
  </div>
</template>
