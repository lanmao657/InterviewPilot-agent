<script setup lang="ts">
import { cn } from '@/lib/utils'

defineProps<{ class?: string }>()
</script>

<template>
  <input
    :class="
      cn(
        'focus-ring flex h-10 w-full rounded-md border bg-card px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
        $props.class,
      )
    "
  />
</template>
