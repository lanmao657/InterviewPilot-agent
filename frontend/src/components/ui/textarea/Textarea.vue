<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    class?: string
    placeholder?: string
    disabled?: boolean
  }>(),
  {
    class: '',
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <textarea
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="cn(
      'flex min-h-24 w-full rounded-[var(--radius-md)] border border-[var(--border-strong)] bg-[var(--bg-input)] px-3.5 py-3 text-sm leading-6',
      'transition-colors duration-150',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'resize-none',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
</template>
