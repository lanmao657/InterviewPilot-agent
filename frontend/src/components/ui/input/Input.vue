<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    modelValue?: string | number
    class?: string
    type?: string
    placeholder?: string
    readonly?: boolean
    disabled?: boolean
    min?: number | string
    max?: number | string
    autocomplete?: string
  }>(),
  {
    type: 'text',
    class: '',
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string | number] }>()
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :readonly="readonly"
    :disabled="disabled"
    :min="min"
    :max="max"
    :autocomplete="autocomplete"
    :class="cn(
      'flex h-11 w-full rounded-[var(--radius-md)] border border-[var(--border-strong)] bg-[var(--bg-input)] px-3.5 py-2 text-sm',
      'transition-colors duration-150',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20',
      'read-only:bg-[var(--surface-muted)] read-only:text-[var(--text-secondary)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
