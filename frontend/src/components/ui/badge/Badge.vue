<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva('inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium', {
  variants: {
    variant: {
      default: 'bg-primary text-primary-foreground',
      secondary: 'bg-secondary text-secondary-foreground',
      outline: 'border bg-card text-foreground',
      accent: 'bg-accent text-accent-foreground',
    },
  },
  defaultVariants: {
    variant: 'secondary',
  },
})

type BadgeVariants = VariantProps<typeof badgeVariants>
const props = withDefaults(defineProps<{ variant?: BadgeVariants['variant']; class?: string }>(), {
  variant: 'secondary',
  class: '',
})
const classes = computed(() => cn(badgeVariants({ variant: props.variant }), props.class))
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
