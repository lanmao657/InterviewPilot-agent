<script setup lang="ts">
defineProps<{ value: number }>()
</script>

<template>
  <div class="h-2 overflow-hidden rounded-full bg-muted">
    <div class="h-full rounded-full bg-primary transition-all" :style="{ width: `${Math.min(100, Math.max(0, value))}%` }" />
  </div>
</template>
