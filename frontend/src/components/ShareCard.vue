<!-- frontend/src/components/ShareCard.vue -->
<!-- 面试准备成绩单分享组件 -->
<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Button } from '@/components/ui/button'

interface Props {
  fitScore: number
  interviewScore: number
  dimensionScores: Record<string, number>
  totalQuestions: number
  reportCount: number
}

const props = defineProps<Props>()
const copied = ref(false)

const dimLabels: Record<string, string> = {
  clarity: '表达清晰度',
  structure: '结构化程度',
  evidence: '证据充分度',
  reflection: '复盘深度',
}

// 生成分享文本
const shareText = computed(() => {
  const lines = [
    '🎯 InterviewPilot 面试准备成绩单',
    '━'.repeat(24),
    `📊 岗位匹配度：${props.fitScore}/100`,
    `🏆 面试综合分：${props.interviewScore}/100`,
    '',
    '📈 各维度得分：',
  ]
  for (const [key, label] of Object.entries(dimLabels)) {
    const score = props.dimensionScores[key] ?? 0
    const bar = '█'.repeat(Math.round(score / 10)) + '░'.repeat(10 - Math.round(score / 10))
    lines.push(`  ${label} ${bar} ${score}`)
  }
  lines.push('')
  lines.push(`📝 已完成 ${props.totalQuestions} 道题 · ${props.reportCount} 份复盘报告`)
  lines.push('')
  lines.push('来自 InterviewPilot — AI 面试准备平台')
  return lines.join('\n')
})

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(shareText.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = shareText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}
</script>

<template>
  <div class="glass rounded-2xl p-5">
    <div class="mb-4 flex items-center justify-between">
      <div>
        <h3 class="text-base font-semibold">面试准备成绩单</h3>
        <p class="text-xs text-[var(--text-muted)]">一键复制，分享你的准备成果</p>
      </div>
      <Button size="sm" variant="secondary" @click="copyToClipboard">
        <Check v-if="copied" class="size-3.5 text-[var(--success)]" />
        <Copy v-else class="size-3.5" />
        {{ copied ? '已复制' : '复制' }}
      </Button>
    </div>

    <!-- 预览卡片 -->
    <div class="rounded-xl bg-gradient-to-br from-[var(--primary)]/5 to-[var(--accent)]/5 p-4 font-mono text-xs leading-5 whitespace-pre-wrap border border-[var(--border)]">
      {{ shareText }}
    </div>
  </div>
</template>
