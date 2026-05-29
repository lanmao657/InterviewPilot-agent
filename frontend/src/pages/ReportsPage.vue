<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { FileBarChart } from 'lucide-vue-next'
import { computed } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import RadarChart from '@/components/charts/RadarChart.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import { api } from '@/lib/api'

const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const averageScores = computed(() => {
  const latest = reportsQuery.data.value?.[0]
  if (!latest?.metrics) return { clarity: 0, structure: 0, evidence: 0, reflection: 0 }
  return {
    clarity: latest.metrics['表达结构'] ?? 0,
    structure: latest.metrics['岗位匹配'] ?? 0,
    evidence: latest.metrics['证据质量'] ?? 0,
    reflection: latest.metrics['复盘深度'] ?? 0,
  }
})

const scoreTrend = computed(() => {
  const reports = reportsQuery.data.value
  if (!reports?.length) return []
  return [...reports]
    .reverse()
    .slice(-10)
    .map((report, i) => ({
      date: `第${i + 1}次`,
      score: report.overall_score,
    }))
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 图表区域 -->
    <div class="grid gap-4 md:grid-cols-2">
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">能力维度分析</h3>
        <RadarChart :data="averageScores" />
      </div>
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">分数趋势</h3>
        <TrendChart :data="scoreTrend" />
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
