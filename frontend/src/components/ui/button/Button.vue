<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'focus-ring inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 active:scale-95',
  {
    variants: {
      variant: {
        default:
          'bg-gradient-to-r from-[var(--primary)] to-[var(--primary-dark)] text-white shadow-md hover:shadow-lg hover:-translate-y-0.5',
        secondary:
          'glass hover:bg-[var(--glass-bg-hover)] hover:-translate-y-0.5',
        outline:
          'border border-[var(--glass-border)] bg-transparent hover:bg-[var(--glass-bg)] hover:-translate-y-0.5',
        ghost:
          'hover:bg-[var(--glass-bg)] hover:-translate-y-0.5',
        destructive:
          'bg-[var(--error)] text-white hover:bg-[var(--error)]/90 hover:-translate-y-0.5',
      },
      size: {
        default: 'h-10 px-5 py-2',
        sm: 'h-9 rounded-lg px-3',
        lg: 'h-12 rounded-xl px-7',
        icon: 'size-10',
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
