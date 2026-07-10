<script setup lang="ts">
import { cn } from '@/lib/utils'

type GlassVariant = 'default' | 'elevated' | 'flat'

const props = withDefaults(
  defineProps<{
    variant?: GlassVariant
    hoverable?: boolean
    class?: string
  }>(),
  {
    variant: 'default',
    hoverable: false,
    class: '',
  },
)

const variantClasses: Record<GlassVariant, string> = {
  default: 'surface',
  elevated: 'surface-raised',
  flat: 'surface-muted',
}
</script>

<template>
  <section
    :class="cn(
      'rounded-[var(--radius-lg)] p-0 transition-colors duration-150',
      variantClasses[variant],
      hoverable && 'hover:border-[var(--border-strong)] cursor-pointer',
      $props.class,
    )"
  >
    <slot />
  </section>
</template>
