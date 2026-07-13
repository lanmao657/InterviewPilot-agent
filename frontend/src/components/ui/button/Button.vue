<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'focus-ring inline-flex min-h-11 items-center justify-center gap-2 rounded-[var(--radius-md)] text-sm font-semibold transition-colors duration-150 disabled:pointer-events-none disabled:opacity-45 active:opacity-80',
  {
    variants: {
      variant: {
        default:
          'border border-[var(--primary)] bg-[var(--primary)] text-[var(--text-on-primary)] shadow-sm hover:bg-[var(--primary-dark)]',
        secondary:
          'border border-[var(--border-strong)] bg-[var(--surface)] text-[var(--text-primary)] hover:bg-[var(--surface-muted)]',
        outline:
          'border border-[var(--border-strong)] bg-transparent text-[var(--text-primary)] hover:bg-[var(--surface-muted)]',
        ghost:
          'text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--text-primary)]',
        destructive:
          'border border-[var(--error)] bg-[var(--error)] text-white hover:opacity-90',
      },
      size: {
        default: 'px-5 py-2',
        sm: 'px-3 py-2 text-xs',
        lg: 'min-h-12 px-7',
        icon: 'size-11 p-0',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

type ButtonVariants = VariantProps<typeof buttonVariants>

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariants['variant']
    size?: ButtonVariants['size']
    class?: string
    type?: 'button' | 'submit' | 'reset'
  }>(),
  {
    variant: 'default',
    size: 'default',
    type: 'button',
    class: '',
  },
)

const classes = computed(() => cn(buttonVariants({ variant: props.variant, size: props.size }), props.class))
</script>

<template>
  <button :type="type" :class="classes">
    <slot />
  </button>
</template>
