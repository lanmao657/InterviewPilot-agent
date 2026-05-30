<!-- frontend/src/components/AnswerCard.vue -->
<!-- 面试话术卡片组件 -->
<script setup lang="ts">
import { Star, Tag } from 'lucide-vue-next'

interface CardData {
  question: string
  star_hint: string
  keywords: string[]
  sample_opening: string
}

defineProps<{ cards: CardData[] }>()
</script>

<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="(card, i) in cards"
      :key="i"
      class="glass-flat rounded-xl p-5 break-inside-avoid"
    >
      <!-- 题目 -->
      <div class="mb-3 flex items-start gap-2">
        <span class="shrink-0 grid size-6 place-items-center rounded-full bg-[var(--primary)]/10 text-xs font-bold text-[var(--primary)]">
          {{ i + 1 }}
        </span>
        <p class="text-sm font-semibold leading-5">{{ card.question }}</p>
      </div>

      <!-- 参考开头 -->
      <div class="mb-3 rounded-lg bg-[var(--primary)]/5 p-3">
        <p class="mb-1 text-xs font-semibold text-[var(--primary)]">参考开头</p>
        <p class="text-sm italic text-[var(--text-secondary)]">"{{ card.sample_opening }}"</p>
      </div>

      <!-- STAR 提示 -->
      <div class="mb-3 flex items-start gap-2">
        <Star class="mt-0.5 size-3.5 shrink-0 text-[var(--warning)]" />
        <p class="text-xs leading-5 text-[var(--text-secondary)]">{{ card.star_hint }}</p>
      </div>

      <!-- 关键词 -->
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="kw in card.keywords"
          :key="kw"
          class="inline-flex items-center gap-1 rounded-full bg-[var(--accent)]/10 px-2 py-0.5 text-[11px] text-[var(--accent)]"
        >
          <Tag class="size-2.5" />
          {{ kw }}
        </span>
      </div>
    </div>
    <p v-if="!cards?.length" class="text-sm text-[var(--text-muted)]">暂无话术卡片数据</p>
  </div>
</template>
