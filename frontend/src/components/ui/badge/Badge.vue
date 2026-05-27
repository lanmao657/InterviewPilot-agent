<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[var(--primary)]/10 text-[var(--primary)]',
        secondary: 'bg-[var(--text-muted)]/10 text-[var(--text-secondary)]',
        outline: 'border border-[var(--glass-border)] text-[var(--text-secondary)]',
        accent: 'bg-[var(--accent)]/10 text-[var(--accent)]',
        success: 'bg-[var(--success)]/10 text-[var(--success)]',
        warning: 'bg-[var(--warning)]/10 text-[var(--warning)]',
        error: 'bg-[var(--error)]/10 text-[var(--error)]',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

type BadgeVariants = VariantProps<typeof badgeVariants>

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariants['variant']
    class?: string
  }>(),
  {
    variant: 'default',
    class: '',
  },
)

const classes = computed(() => cn(badgeVariants({ variant: props.variant }), props.class))
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
