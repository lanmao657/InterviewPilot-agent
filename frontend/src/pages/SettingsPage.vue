<script setup lang="ts">
import { Input } from '@/components/ui/input'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="glass rounded-2xl p-6">
    <h2 class="text-lg font-semibold">设置</h2>
    <p class="mb-5 text-sm text-[var(--text-secondary)]">模型配置通过后端环境变量管理，前端只展示当前说明。</p>

    <div class="grid gap-4 md:grid-cols-2">
      <label class="flex flex-col gap-2 text-sm font-medium">
        API 地址
        <Input model-value="VITE_API_BASE_URL=http://localhost:8000/api" readonly />
      </label>
      <label class="flex flex-col gap-2 text-sm font-medium">
        模型配置
        <Input model-value="AI_BASE_URL / AI_API_KEY / AI_MODEL" readonly />
      </label>
    </div>

    <div class="mt-6 flex items-center gap-3">
      <span class="text-sm font-medium">主题</span>
      <ThemeToggle />
      <span class="text-sm text-[var(--text-muted)]">{{ theme.theme === 'system' ? '跟随系统' : theme.resolved === 'dark' ? '深色' : '浅色' }}</span>
    </div>
  </div>
</template>
