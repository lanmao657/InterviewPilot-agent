<script setup lang="ts">
import {
  BarChart3,
  BookOpenCheck,
  Bot,
  FileText,
  Gauge,
  LogOut,
  MessageSquareText,
  Settings,
  UserCircle,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import GlobalAssistantWidget from '@/components/assistant/GlobalAssistantWidget.vue'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const navItems = [
  { label: '仪表盘', path: '/dashboard', icon: Gauge },
  { label: '简历与 JD', path: '/documents', icon: FileText },
  { label: '题库', path: '/questions', icon: BookOpenCheck },
  { label: '模拟面试', path: '/interview', icon: MessageSquareText },
  { label: 'AI 助手', path: '/assistant', icon: Bot },
  { label: '报告', path: '/reports', icon: BarChart3 },
  { label: '设置', path: '/settings', icon: Settings },
]

const pageTitle = computed(() => navItems.find((item) => route.path.startsWith(item.path))?.label ?? '仪表盘')

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex min-h-screen">
    <aside class="hidden w-64 shrink-0 border-r bg-card/88 px-4 py-5 shadow-sm backdrop-blur lg:flex lg:flex-col">
      <div class="flex items-center gap-3 px-2">
        <div class="grid size-10 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">IP</div>
        <div>
          <p class="text-base font-semibold">InterviewPilot</p>
          <p class="text-xs text-muted-foreground">AI 面试准备</p>
        </div>
      </div>

      <nav class="mt-8 flex flex-col gap-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          :class="{ 'bg-accent text-accent-foreground': route.path.startsWith(item.path) }"
        >
          <component :is="item.icon" data-icon="inline-start" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="mt-auto rounded-lg border bg-background/70 p-3">
        <div class="flex items-center gap-3">
          <UserCircle class="text-muted-foreground" />
          <div class="min-w-0">
            <p class="truncate text-sm font-medium">{{ auth.user?.name }}</p>
            <p class="truncate text-xs text-muted-foreground">{{ auth.user?.username }}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" class="mt-3 w-full justify-start" @click="logout">
          <LogOut data-icon="inline-start" />
          退出登录
        </Button>
      </div>
    </aside>

    <main class="min-w-0 flex-1">
      <header class="sticky top-0 z-10 border-b bg-background/82 px-5 py-4 backdrop-blur">
        <div class="mx-auto flex max-w-7xl items-center justify-between gap-3">
          <div>
            <p class="text-xs font-medium text-muted-foreground">InterviewPilot</p>
            <h1 class="text-xl font-semibold">{{ pageTitle }}</h1>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" @click="router.push('/assistant')">
              <Bot data-icon="inline-start" />
              AI 助手
            </Button>
            <Button size="sm" @click="router.push('/interview')">
              <MessageSquareText data-icon="inline-start" />
              开始练习
            </Button>
          </div>
        </div>
      </header>
      <div class="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <RouterView />
      </div>
    </main>
    <GlobalAssistantWidget />
  </div>
</template>
