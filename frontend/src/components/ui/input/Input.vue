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
      'flex h-10 w-full rounded-xl border border-[var(--glass-border)] bg-[var(--bg-input)] px-4 py-2 text-sm',
      'backdrop-blur-sm transition-all duration-200',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:ring-4 focus:ring-[var(--primary)]/10 focus:bg-[var(--bg-elevated)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
