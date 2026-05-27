<script setup lang="ts">
import { cn } from '@/lib/utils'

defineProps<{ class?: string }>()
</script>

<template>
  <section :class="cn('glass rounded-2xl text-sm', $props.class)">
    <slot />
  </section>
</template>
