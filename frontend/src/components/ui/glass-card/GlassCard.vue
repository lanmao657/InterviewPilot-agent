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
  default: 'glass',
  elevated: 'glass-elevated',
  flat: 'glass-flat',
}
</script>

<template>
  <section
    :class="cn(
      'rounded-2xl p-0 transition-all duration-200',
      variantClasses[variant],
      hoverable && 'hover:-translate-y-0.5 hover:shadow-lg cursor-pointer',
      $props.class,
    )"
  >
    <slot />
  </section>
</template>
