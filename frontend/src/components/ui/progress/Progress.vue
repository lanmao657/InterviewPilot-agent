<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    value?: number
    label?: string
    class?: string
  }>(),
  {
    value: 0,
    label: '进度',
    class: '',
  },
)

const clampedValue = computed(() => Math.min(100, Math.max(0, props.value)))
</script>

<template>
  <div
    :class="cn('h-2 w-full overflow-hidden rounded-full bg-[var(--surface-muted)]', $props.class)"
    role="progressbar"
    :aria-label="label"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-valuenow="clampedValue"
  >
    <div
      class="h-full rounded-full bg-[var(--primary)] transition-[width] duration-200 ease-out"
      :style="{ width: `${clampedValue}%` }"
    />
  </div>
</template>
