<!-- frontend/src/components/ui/toast/ToastContainer.vue -->
<!-- 全局 Toast 通知容器，挂在 AppShell 中 -->
<script setup lang="ts">
import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-vue-next'
import { useToastStore, type ToastType } from '@/stores/toast'

const toast = useToastStore()

const iconMap: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const colorMap: Record<ToastType, string> = {
  success: 'var(--success)',
  error: 'var(--error)',
  warning: 'var(--warning)',
  info: 'var(--primary)',
}
</script>

<template>
  <div class="fixed right-4 top-4 z-[200] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="t in toast.toasts"
        :key="t.id"
        class="pointer-events-auto glass-elevated flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg min-w-64 max-w-sm"
        :style="{ borderLeft: `3px solid ${colorMap[t.type]}` }"
      >
        <component :is="iconMap[t.type]" class="size-4 shrink-0" :style="{ color: colorMap[t.type] }" />
        <p class="flex-1 text-sm">{{ t.message }}</p>
        <button class="shrink-0 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors" @click="toast.dismiss(t.id)">
          <X class="size-3.5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active {
  animation: toast-in 250ms ease-out;
}
.toast-leave-active {
  animation: toast-out 200ms ease-in;
}
@keyframes toast-in {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes toast-out {
  from { opacity: 1; transform: translateX(0); }
  to { opacity: 0; transform: translateX(100%); }
}
</style>
