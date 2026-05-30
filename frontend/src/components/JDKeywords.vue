<!-- frontend/src/components/JDKeywords.vue -->
<!-- JD 关键词标签云组件 -->
<script setup lang="ts">
import { computed } from 'vue'

export interface Keyword {
  term: string
  category: string
  importance: 'high' | 'medium' | 'low'
}

const props = defineProps<{ keywords: Keyword[] }>()

// 按重要度排序
const sortedKeywords = computed(() =>
  [...(props.keywords ?? [])].sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 }
    return (order[a.importance] ?? 2) - (order[b.importance] ?? 2)
  })
)

// 根据分类返回颜色
function categoryColor(category: string): string {
  const map: Record<string, string> = {
    '技术': 'var(--primary)',
    '软技能': 'var(--accent)',
    '经验': 'var(--warning)',
    '学历': 'var(--success)',
  }
  return map[category] ?? 'var(--text-muted)'
}

// 根据重要度返回标签
function importanceLabel(importance: string): string {
  if (importance === 'high') return '核心'
  if (importance === 'medium') return '重要'
  return '加分'
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <span
      v-for="kw in sortedKeywords"
      :key="kw.term"
      class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm transition-all hover:scale-105"
      :style="{
        background: `${categoryColor(kw.category)}10`,
        border: `1px solid ${categoryColor(kw.category)}30`,
        color: categoryColor(kw.category),
      }"
    >
      {{ kw.term }}
      <span class="text-[10px] opacity-60">{{ importanceLabel(kw.importance) }}</span>
    </span>
    <p v-if="!keywords?.length" class="text-sm text-[var(--text-muted)]">暂无关键词数据</p>
  </div>
</template>
