<script setup lang="ts">
import { cn } from '@/lib/utils'

defineProps<{ class?: string }>()
</script>

<template>
  <textarea
    :class="
      cn(
        'focus-ring min-h-28 w-full rounded-md border bg-card px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
        $props.class,
      )
    "
  />
</template>
