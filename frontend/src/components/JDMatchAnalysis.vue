<!-- frontend/src/components/JDMatchAnalysis.vue -->
<!-- JD 匹配差距分析组件 -->
<script setup lang="ts">
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-vue-next'

interface MatchItem {
  requirement: string
  evidence: string
}

interface GapItem {
  requirement: string
  severity: 'high' | 'medium' | 'low'
  suggestion: string
}

interface MatchData {
  matched: MatchItem[]
  gaps: GapItem[]
  summary: string
}

defineProps<{ data: MatchData }>()

// 严重程度颜色映射
const severityColors: Record<string, string> = {
  high: 'var(--error)',
  medium: 'var(--warning)',
  low: 'var(--text-muted)',
}
const severityLabels: Record<string, string> = {
  high: '核心缺失',
  medium: '重要',
  low: '加分项',
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- 匹配总览 -->
    <div class="flex items-center gap-3 rounded-xl glass-flat p-3">
      <div class="flex items-center gap-4 text-sm">
        <span class="flex items-center gap-1 text-[var(--success)]">
          <CheckCircle class="size-4" /> 已覆盖 {{ data.matched?.length ?? 0 }}
        </span>
        <span class="flex items-center gap-1 text-[var(--error)]">
          <XCircle class="size-4" /> 缺失 {{ data.gaps?.length ?? 0 }}
        </span>
      </div>
    </div>

    <!-- AI 总结 -->
    <p class="text-sm text-[var(--text-secondary)]">{{ data.summary }}</p>

    <!-- 已覆盖要求 -->
    <div v-if="data.matched?.length" class="flex flex-col gap-2">
      <p class="flex items-center gap-1.5 text-sm font-semibold text-[var(--success)]">
        <CheckCircle class="size-4" />
        已覆盖的 JD 要求
      </p>
      <div v-for="(item, i) in data.matched" :key="i" class="rounded-lg glass-flat p-3">
        <p class="text-sm font-medium">{{ item.requirement }}</p>
        <p class="mt-1 text-xs text-[var(--text-muted)]">简历证据：{{ item.evidence }}</p>
      </div>
    </div>

    <!-- 缺失要求 -->
    <div v-if="data.gaps?.length" class="flex flex-col gap-2">
      <p class="flex items-center gap-1.5 text-sm font-semibold text-[var(--error)]">
        <AlertTriangle class="size-4" />
        需要弥补的差距
      </p>
      <div v-for="(item, i) in data.gaps" :key="i" class="rounded-lg glass-flat p-3">
        <div class="mb-1 flex items-center gap-2">
          <span
            class="rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
            :style="{ background: severityColors[item.severity] ?? 'var(--text-muted)' }"
          >
            {{ severityLabels[item.severity] ?? item.severity }}
          </span>
          <p class="text-sm font-medium">{{ item.requirement }}</p>
        </div>
        <p class="text-xs text-[var(--primary)]">建议：{{ item.suggestion }}</p>
      </div>
    </div>
  </div>
</template>
