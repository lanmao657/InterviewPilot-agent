<script setup lang="ts">
import {
  AlertTriangle,
  BarChart3,
  BookOpenCheck,
  Bot,
  FileText,
  Gauge,
  LogOut,
  Menu,
  MessageSquareText,
  Settings,
  UserCircle,
  X,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import GlobalAssistantWidget from '@/components/assistant/GlobalAssistantWidget.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)
const showGuestLogoutConfirm = ref(false)

const navItems = [
  { label: '仪表盘', path: '/dashboard', icon: Gauge },
  { label: '简历与 JD', path: '/documents', icon: FileText },
  { label: '题库', path: '/questions', icon: BookOpenCheck },
  { label: '模拟面试', path: '/interview', icon: MessageSquareText },
  { label: 'AI 助手', path: '/assistant', icon: Bot },
  { label: '报告', path: '/reports', icon: BarChart3 },
  { label: '设置', path: '/settings', icon: Settings },
]

const mobileNavItems = navItems.slice(0, 5)

const pageTitle = computed(() => navItems.find((item) => route.path.startsWith(item.path))?.label ?? '仪表盘')

function logout() {
  if (auth.isGuest) {
    showGuestLogoutConfirm.value = true
    return
  }
  auth.logout()
  router.push('/login')
}

function confirmGuestLogout() {
  showGuestLogoutConfirm.value = false
  auth.logout()
  router.push('/login')
}

function cancelGuestLogout() {
  showGuestLogoutConfirm.value = false
}

function closeSidebar() {
  sidebarOpen.value = false
}
</script>

<template>
  <div class="flex min-h-screen">
    <!-- 移动端遮罩 -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
        @click="closeSidebar"
      />
    </Transition>

    <!-- 侧边栏 -->
    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col glass-elevated transition-transform duration-300 lg:static lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="flex items-center justify-between gap-3 px-5 py-5">
        <div class="flex items-center gap-3">
          <div class="grid size-10 place-items-center rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-sm font-bold text-white shadow-md">
            IP
          </div>
          <div>
            <p class="text-base font-semibold">InterviewPilot</p>
            <p class="text-xs text-[var(--text-muted)]">AI 面试准备</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="lg:hidden" @click="closeSidebar">
          <X class="size-5" />
        </Button>
      </div>

      <!-- 导航 -->
      <nav class="mt-4 flex flex-1 flex-col gap-1 px-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="group relative flex h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-[var(--text-secondary)] transition-all duration-200 hover:bg-[var(--glass-bg-hover)] hover:text-[var(--text-primary)]"
          :class="{ 'bg-[var(--primary)]/10 text-[var(--primary)]': route.path.startsWith(item.path) }"
          @click="closeSidebar"
        >
          <div
            v-if="route.path.startsWith(item.path)"
            class="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-[var(--primary)]"
          />
          <component :is="item.icon" class="size-5" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- 用户信息 -->
      <div class="mx-3 mb-4 rounded-xl glass-flat p-3">
        <div class="flex items-center gap-3">
          <div class="grid size-9 place-items-center rounded-full bg-[var(--primary)]/10">
            <UserCircle class="size-5 text-[var(--primary)]" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium">{{ auth.user?.name }}</p>
            <p class="truncate text-xs text-[var(--text-muted)]">{{ auth.user?.username }}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" class="mt-2 w-full justify-start" @click="logout">
          <LogOut class="size-4" />
          退出登录
        </Button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="flex min-w-0 flex-1 flex-col">
      <!-- 游客提示横幅 -->
      <Transition name="fade">
        <div
          v-if="auth.isGuest"
          class="flex items-center justify-center gap-2 border-b border-[var(--warning)]/30 bg-[var(--warning)]/10 px-4 py-2 text-sm"
        >
          <AlertTriangle class="size-4 text-[var(--warning)]" />
          <span class="text-[var(--text-secondary)]">当前为游客模式，数据仅在本次会话中保存</span>
          <Button variant="ghost" size="sm" @click="router.push('/login')">
            注册正式账号
          </Button>
        </div>
      </Transition>

      <!-- Header -->
      <header class="sticky top-0 z-30 glass border-b border-[var(--glass-border)]">
        <div class="mx-auto flex max-w-7xl items-center justify-between gap-3 px-5 py-3">
          <div class="flex items-center gap-3">
            <Button variant="ghost" size="icon" class="lg:hidden" @click="sidebarOpen = true">
              <Menu class="size-5" />
            </Button>
            <div>
              <p class="text-xs font-medium text-[var(--text-muted)]">InterviewPilot</p>
              <h1 class="text-lg font-semibold">{{ pageTitle }}</h1>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="secondary" size="sm" class="hidden sm:inline-flex" @click="router.push('/assistant')">
              <Bot class="size-4" />
              AI 助手
            </Button>
            <Button size="sm" @click="router.push('/interview')">
              <MessageSquareText class="size-4" />
              <span class="hidden sm:inline">开始练习</span>
            </Button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="mx-auto w-full max-w-7xl flex-1 px-4 py-5 sm:px-6 lg:px-8">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>

      <!-- 移动端底部导航 -->
      <nav class="fixed bottom-0 left-0 right-0 z-30 glass border-t border-[var(--glass-border)] pb-[env(safe-area-inset-bottom)] lg:hidden">
        <div class="flex items-center justify-around px-2 py-2">
          <RouterLink
            v-for="item in mobileNavItems"
            :key="item.path"
            :to="item.path"
            class="flex flex-col items-center gap-0.5 rounded-lg px-3 py-1.5 text-[10px] font-medium transition-colors"
            :class="route.path.startsWith(item.path) ? 'text-[var(--primary)]' : 'text-[var(--text-muted)]'"
          >
            <component :is="item.icon" class="size-5" />
            {{ item.label }}
          </RouterLink>
        </div>
      </nav>

      <!-- 移动端底部导航占位 -->
      <div class="h-16 lg:hidden" />
    </main>

    <GlobalAssistantWidget />

    <!-- 游客退出确认对话框 -->
    <Transition name="fade">
      <div
        v-if="showGuestLogoutConfirm"
        class="fixed inset-0 z-[100] grid place-items-center bg-black/50 backdrop-blur-sm"
        @click.self="cancelGuestLogout"
      >
        <div class="glass-elevated mx-4 w-full max-w-sm rounded-2xl p-6 animate-fade-in-up">
          <div class="mb-4 flex items-center gap-3">
            <div class="grid size-10 place-items-center rounded-full bg-[var(--warning)]/10">
              <AlertTriangle class="size-5 text-[var(--warning)]" />
            </div>
            <div>
              <h3 class="font-semibold">确认退出游客模式？</h3>
              <p class="mt-1 text-xs text-[var(--text-muted)]">游客数据将在 24 小时后清除</p>
            </div>
          </div>
          <p class="mb-5 text-sm text-[var(--text-secondary)]">
            你上传的简历、面试记录和复盘报告将会丢失。建议注册正式账号保存数据。
          </p>
          <div class="flex gap-3">
            <Button class="flex-1" @click="router.push('/login'); showGuestLogoutConfirm = false">
              注册正式账号
            </Button>
            <Button variant="secondary" class="flex-1" @click="confirmGuestLogout">
              仍然退出
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active {
  animation: fade-in-up 300ms ease-out;
}
.page-leave-active {
  animation: fade-out-up 200ms ease-in;
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-out-up {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-8px); }
}
</style>
