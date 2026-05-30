<!-- frontend/src/components/ProgressGuide.vue -->
<!-- 全局进度引导条：展示面试准备全流程 -->
<script setup lang="ts">
import { Check, ChevronRight } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

interface StepData {
  label: string
  path: string
  done: boolean
}

const props = defineProps<{ steps: StepData[] }>()
const router = useRouter()

// 当前第一个未完成的步骤索引
const currentStepIndex = computed(() => {
  const idx = props.steps.findIndex((s) => !s.done)
  return idx === -1 ? props.steps.length - 1 : idx
})

// 总体进度百分比
const progress = computed(() => {
  const done = props.steps.filter((s) => s.done).length
  return Math.round((done / props.steps.length) * 100)
})
</script>

<template>
  <div class="glass rounded-2xl p-5">
    <div class="mb-3 flex items-center justify-between">
      <p class="text-sm font-semibold">面试准备进度</p>
      <span class="text-xs text-[var(--text-muted)]">{{ progress }}% 完成</span>
    </div>

    <!-- 进度条 -->
    <div class="mb-4 h-1.5 overflow-hidden rounded-full bg-[var(--bg-input)]">
      <div
        class="h-full rounded-full bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] transition-all duration-500"
        :style="{ width: `${progress}%` }"
      />
    </div>

    <!-- 步骤列表 -->
    <div class="flex flex-wrap items-center gap-1">
      <template v-for="(step, i) in steps" :key="step.label">
        <button
          class="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all"
          :class="step.done
            ? 'text-[var(--success)] bg-[var(--success)]/10'
            : i === currentStepIndex
              ? 'text-[var(--primary)] bg-[var(--primary)]/10 ring-1 ring-[var(--primary)]/30 animate-pulse'
              : 'text-[var(--text-muted)] hover:bg-[var(--glass-bg-hover)]'"
          @click="router.push(step.path)"
        >
          <Check v-if="step.done" class="size-3" />
          <span v-else class="size-3 rounded-full border border-current" />
          {{ step.label }}
        </button>
        <ChevronRight v-if="i < steps.length - 1" class="size-3 text-[var(--text-muted)]" />
      </template>
    </div>
  </div>
</template>
