<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowDownRight, ArrowUpRight, FileBarChart, Printer } from 'lucide-vue-next'
import { computed, defineAsyncComponent } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import ShareCard from '@/components/ShareCard.vue'
import { api } from '@/lib/api'

const RadarChart = defineAsyncComponent(() => import('@/components/charts/RadarChart.vue'))
const TrendChart = defineAsyncComponent(() => import('@/components/charts/TrendChart.vue'))

const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })
const trendQuery = useQuery({ queryKey: ['report-trend'], queryFn: api.reportTrend })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const historyQuery = useQuery({ queryKey: ['answer-history'], queryFn: api.answerHistory })

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

// 分享成绩单数据
const shareData = computed(() => {
  const latest = reportsQuery.data.value?.[0]
  const activePlan = plansQuery.data.value?.[0]
  return {
    fitScore: activePlan?.fit_score ?? 0,
    interviewScore: latest?.overall_score ?? 0,
    dimensionScores: latest?.metrics ?? {},
    totalQuestions: reportsQuery.data.value?.length ?? 0,
    reportCount: reportsQuery.data.value?.length ?? 0,
  }
})

// 导出 PDF（使用浏览器打印功能）
function exportPDF() {
  const reports = reportsQuery.data.value
  if (!reports?.length) return
  const latest = reports[0]
  const scores = latest.metrics ?? {}
  const dimLabels: Record<string, string> = {
    clarity: '表达清晰度',
    structure: '结构化程度',
    evidence: '证据充分度',
    reflection: '复盘深度',
  }
  const scoreRows = Object.entries(dimLabels)
    .map(([key, label]) => `<tr><td>${label}</td><td style="text-align:right;font-weight:bold">${scores[key] ?? 0} 分</td></tr>`)
    .join('')

  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${latest.title}</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:40px;color:#1a1a1a;max-width:700px;margin:0 auto}
h1{font-size:20px;border-bottom:2px solid #3b82f6;padding-bottom:8px}
.score{font-size:36px;font-weight:bold;color:#3b82f6}
table{width:100%;border-collapse:collapse;margin:16px 0}
td,th{padding:8px 12px;border:1px solid #e5e7eb;text-align:left}
th{background:#f3f4f6;font-weight:600}
.content{white-space:pre-line;line-height:1.8;margin-top:16px}
.footer{margin-top:40px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280}
</style></head><body>
<h1>${latest.title}</h1>
<p>综合得分：<span class="score">${latest.overall_score} 分</span></p>
<table><thead><tr><th>维度</th><th>分数</th></tr></thead><tbody>${scoreRows}</tbody></table>
<div class="content">${latest.content}</div>
<div class="footer">来自 InterviewPilot — AI 面试准备平台 · ${new Date().toLocaleDateString('zh-CN')}</div>
</body></html>`
  const win = window.open('', '_blank')
  if (win) {
    win.document.write(html)
    win.document.close()
    win.print()
  }
}
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

    <!-- 分享成绩单 -->
    <ShareCard v-if="reportsQuery.data.value?.length" v-bind="shareData" />

    <!-- 报告列表 -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">复盘报告</h3>
      <Button
        v-if="reportsQuery.data.value?.length"
        variant="secondary"
        size="sm"
        @click="exportPDF"
      >
        <Printer class="size-3.5" />
        导出 PDF
      </Button>
    </div>
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

    <!-- 面试答案历史对比 -->
    <div v-if="historyQuery.data.value?.length" class="glass rounded-2xl p-5">
      <h3 class="mb-1 text-base font-semibold">答案历史对比</h3>
      <p class="mb-4 text-xs text-[var(--text-muted)]">查看你在不同面试中对同一题的回答和得分变化</p>
      <div class="flex flex-col gap-3">
        <div
          v-for="(item, i) in historyQuery.data.value.slice(0, 10)"
          :key="item.turn_id"
          class="glass-flat rounded-xl p-4 animate-stagger"
          :style="{ '--stagger-index': i }"
        >
          <div class="mb-2 flex items-center justify-between">
            <span class="text-xs text-[var(--text-muted)]">{{ item.interview_title }} · {{ item.created_at?.slice(0, 10) }}</span>
            <Badge variant="accent" class="text-xs">{{ item.score }} 分</Badge>
          </div>
          <p class="mb-1 text-sm font-medium">{{ item.question }}</p>
          <p class="text-xs text-[var(--text-muted)] line-clamp-2">{{ item.answer }}</p>
          <p v-if="item.feedback_summary" class="mt-1 text-xs text-[var(--primary)]">{{ item.feedback_summary }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
