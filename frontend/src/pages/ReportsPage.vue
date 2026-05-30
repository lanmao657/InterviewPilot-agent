<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowDownRight, ArrowUpRight, FileBarChart } from 'lucide-vue-next'
import { computed } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import RadarChart from '@/components/charts/RadarChart.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import { api } from '@/lib/api'

const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })
const trendQuery = useQuery({ queryKey: ['report-trend'], queryFn: api.reportTrend })

// 最新报告的四维分数
const averageScores = computed(() => {
  const latest = reportsQuery.data.value?.[0]
  if (!latest?.metrics) return { clarity: 0, structure: 0, evidence: 0, reflection: 0 }
  return {
    clarity: latest.metrics['clarity'] ?? 0,
    structure: latest.metrics['structure'] ?? 0,
    evidence: latest.metrics['evidence'] ?? 0,
    reflection: latest.metrics['reflection'] ?? 0,
  }
})

// 趋势数据
const trendData = computed(() => (trendQuery.data.value ?? []) as Array<{
  label: string
  overall: number
  clarity?: number
  structure?: number
  evidence?: number
  reflection?: number
}>)

// 计算进步最大和仍需改进的维度
const dimensionAnalysis = computed(() => {
  const data = trendQuery.data.value
  if (!data || data.length < 2) return null

  const first = data[0] as Record<string, number>
  const last = data[data.length - 1] as Record<string, number>
  const dims = ['clarity', 'structure', 'evidence', 'reflection'] as const
  const dimLabels: Record<string, string> = {
    clarity: '表达清晰度',
    structure: '结构化程度',
    evidence: '证据充分度',
    reflection: '复盘深度',
  }

  const changes = dims.map((dim) => ({
    dim,
    label: dimLabels[dim],
    first: first[dim] ?? 0,
    last: last[dim] ?? 0,
    change: (last[dim] ?? 0) - (first[dim] ?? 0),
  }))

  const improved = [...changes].sort((a, b) => b.change - a.change)[0]
  const needsWork = [...changes].sort((a, b) => a.last - b.last)[0]

  return { improved, needsWork }
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 进步/改进维度卡片 -->
    <div v-if="dimensionAnalysis" class="grid gap-4 sm:grid-cols-2">
      <div class="glass rounded-2xl p-4 flex items-center gap-4">
        <div class="grid size-10 place-items-center rounded-full bg-[var(--success)]/10">
          <ArrowUpRight class="size-5 text-[var(--success)]" />
        </div>
        <div>
          <p class="text-xs text-[var(--text-muted)]">进步最大</p>
          <p class="text-sm font-semibold">{{ dimensionAnalysis.improved.label }}</p>
          <p class="text-xs text-[var(--success)]">
            +{{ dimensionAnalysis.improved.change }} 分（{{ dimensionAnalysis.improved.first }} → {{ dimensionAnalysis.improved.last }}）
          </p>
        </div>
      </div>
      <div class="glass rounded-2xl p-4 flex items-center gap-4">
        <div class="grid size-10 place-items-center rounded-full bg-[var(--warning)]/10">
          <ArrowDownRight class="size-5 text-[var(--warning)]" />
        </div>
        <div>
          <p class="text-xs text-[var(--text-muted)]">仍需改进</p>
          <p class="text-sm font-semibold">{{ dimensionAnalysis.needsWork.label }}</p>
          <p class="text-xs text-[var(--warning)]">
            当前 {{ dimensionAnalysis.needsWork.last }} 分
          </p>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid gap-4 md:grid-cols-2">
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">能力维度分析</h3>
        <RadarChart :data="averageScores" />
      </div>
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">多维度趋势</h3>
        <TrendChart v-if="trendData.length" :data="trendData" :multi-dimension="trendData.length >= 2" />
        <div v-else class="flex h-80 items-center justify-center text-sm text-[var(--text-muted)]">
          暂无趋势数据
        </div>
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="grid gap-4 lg:grid-cols-2">
      <div
        v-for="(report, index) in reportsQuery.data.value"
        :key="report.id"
        class="glass rounded-2xl p-5 animate-stagger"
        :style="{ '--stagger-index': index }"
      >
        <div class="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3 class="font-semibold">{{ report.title }}</h3>
            <p class="text-xs text-[var(--text-muted)]">STAR Feedback 复盘</p>
          </div>
          <Badge variant="accent" class="text-sm">{{ report.overall_score }} 分</Badge>
        </div>
        <Progress :value="report.overall_score" class="mb-3" />
        <p class="whitespace-pre-line text-sm leading-6 text-[var(--text-secondary)]">{{ report.content }}</p>
      </div>

      <div v-if="!reportsQuery.data.value?.length" class="glass rounded-2xl p-6 text-center lg:col-span-2">
        <FileBarChart class="mx-auto mb-3 size-8 text-[var(--primary)]" />
        <h3 class="font-semibold">还没有报告</h3>
        <p class="mt-1 text-sm text-[var(--text-muted)]">完成至少一轮模拟面试后生成复盘报告</p>
      </div>
    </div>
  </div>
</template>
