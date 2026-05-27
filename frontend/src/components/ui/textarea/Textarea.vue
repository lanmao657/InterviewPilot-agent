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
      'flex min-h-20 w-full rounded-xl border border-[var(--glass-border)] bg-[var(--bg-input)] px-4 py-3 text-sm',
      'backdrop-blur-sm transition-all duration-200',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:ring-4 focus:ring-[var(--primary)]/10 focus:bg-[var(--bg-elevated)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'resize-none',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
</template>
