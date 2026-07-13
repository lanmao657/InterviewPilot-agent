<script setup lang="ts">
import { cn } from '@/lib/utils'

defineProps<{ class?: string }>()
</script>

<template>
  <section :class="cn('surface rounded-[var(--radius-lg)] text-sm', $props.class)">
    <slot />
  </section>
</template>
