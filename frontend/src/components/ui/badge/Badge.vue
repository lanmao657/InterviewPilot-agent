<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-[var(--radius-sm)] border px-2 py-1 text-xs font-semibold leading-none',
  {
    variants: {
      variant: {
        default: 'border-[var(--primary)]/30 bg-[var(--primary)]/10 text-[var(--primary)]',
        secondary: 'border-[var(--border)] bg-[var(--surface-muted)] text-[var(--text-secondary)]',
        outline: 'border-[var(--border-strong)] bg-transparent text-[var(--text-secondary)]',
        accent: 'border-[var(--accent)]/30 bg-[var(--accent)]/10 text-[var(--accent)]',
        success: 'border-[var(--success)]/30 bg-[var(--success-light)] text-[var(--success)]',
        warning: 'border-[var(--warning)]/30 bg-[var(--warning-light)] text-[var(--warning)]',
        error: 'border-[var(--error)]/30 bg-[var(--error-light)] text-[var(--error)]',
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
