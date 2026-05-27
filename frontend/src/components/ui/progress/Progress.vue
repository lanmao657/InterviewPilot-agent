<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    value?: number
    class?: string
  }>(),
  {
    value: 0,
    class: '',
  },
)
</script>

<template>
  <div :class="cn('h-2 w-full overflow-hidden rounded-full bg-[var(--glass-bg)]', $props.class)">
    <div
      class="h-full rounded-full bg-gradient-to-r from-[var(--primary)] to-[var(--primary-dark)] transition-all duration-500 ease-out"
      :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"
    />
  </div>
</template>
