<script setup lang="ts">
import { ServerCog, ShieldCheck, SunMoon } from 'lucide-vue-next'

import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { Badge } from '@/components/ui/badge'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="mx-auto flex max-w-4xl flex-col gap-8">
    <section>
      <p class="eyebrow">个人偏好</p>
      <h2 class="mt-2 text-3xl font-semibold">设置</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">调整阅读体验，查看当前服务连接状态。</p>
    </section>

    <section class="surface overflow-hidden rounded-[var(--radius-lg)]">
      <div class="flex flex-col gap-4 border-b border-[var(--border)] p-6 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex gap-3">
          <SunMoon class="mt-0.5 size-5 shrink-0 text-[var(--primary)]" />
          <div>
            <h3 class="text-lg font-semibold">界面主题</h3>
            <p class="mt-1 text-sm text-[var(--text-secondary)]">可手动选择，或跟随系统外观。</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <ThemeToggle />
          <Badge variant="outline">{{ theme.theme === 'system' ? '跟随系统' : theme.resolved === 'dark' ? '深色' : '浅色' }}</Badge>
        </div>
      </div>

      <div class="flex flex-col gap-4 border-b border-[var(--border)] p-6 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex gap-3">
          <ServerCog class="mt-0.5 size-5 shrink-0 text-[var(--accent)]" />
          <div>
            <h3 class="text-lg font-semibold">服务连接</h3>
            <p class="mt-1 text-sm text-[var(--text-secondary)]">接口和模型由服务端安全管理，前端不会展示密钥或私有地址。</p>
          </div>
        </div>
        <Badge variant="success">由服务端管理</Badge>
      </div>

      <div class="flex gap-3 p-6">
        <ShieldCheck class="mt-0.5 size-5 shrink-0 text-[var(--success)]" />
        <div>
          <h3 class="text-lg font-semibold">数据说明</h3>
          <p class="mt-1 text-sm leading-6 text-[var(--text-secondary)]">正式账号会保存材料与训练记录；游客数据仅用于当前体验，并按服务端策略清理。</p>
        </div>
      </div>
    </section>
  </div>
</template>
