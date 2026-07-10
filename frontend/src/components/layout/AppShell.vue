<script setup lang="ts">
import {
  AlertTriangle,
  BarChart3,
  BookOpenCheck,
  FileText,
  Gauge,
  LogOut,
  Menu,
  MessageCircleQuestion,
  MessageSquareText,
  Settings,
  UserCircle,
  X,
} from 'lucide-vue-next'
import { computed, nextTick, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { Button } from '@/components/ui/button'
import ToastContainer from '@/components/ui/toast/ToastContainer.vue'
import { useAuthStore } from '@/stores/auth'

type NavItem = {
  label: string
  shortLabel?: string
  path: string
  icon: typeof Gauge
  description: string
}

type NavGroup = {
  label: '准备' | '训练' | '复盘'
  items: NavItem[]
}

const overviewItem: NavItem = {
  label: '概览',
  path: '/dashboard',
  icon: Gauge,
  description: '查看当前阶段与下一项准备任务',
}

const navGroups: NavGroup[] = [
  {
    label: '准备',
    items: [
      { label: '材料工作区', shortLabel: '材料', path: '/documents', icon: FileText, description: '整理简历、岗位描述与准备计划' },
    ],
  },
  {
    label: '训练',
    items: [
      { label: '题库', path: '/questions', icon: BookOpenCheck, description: '生成并筛选针对性面试题' },
      { label: '模拟面试', shortLabel: '面试', path: '/interview', icon: MessageSquareText, description: '练习回答并获得即时反馈' },
    ],
  },
  {
    label: '复盘',
    items: [
      { label: '能力报告', shortLabel: '报告', path: '/reports', icon: BarChart3, description: '查看表现趋势与下一步改进重点' },
    ],
  },
]

const settingsItem: NavItem = {
  label: '设置',
  path: '/settings',
  icon: Settings,
  description: '管理主题与产品配置说明',
}

const coachItem: NavItem = {
  label: '教练对话',
  path: '/assistant',
  icon: MessageCircleQuestion,
  description: '结合你的材料与训练记录获得建议',
}

const allItems = [overviewItem, ...navGroups.flatMap((group) => group.items), coachItem, settingsItem]
const mobileNavItems = [overviewItem, navGroups[0].items[0], navGroups[1].items[0], navGroups[1].items[1], navGroups[2].items[0]]

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)
const showGuestLogoutConfirm = ref(false)
const mainContent = ref<HTMLElement | null>(null)
const guestDialog = ref<HTMLElement | null>(null)

const currentPage = computed(() => {
  if (route.path.startsWith('/plans/')) {
    return { label: '准备计划', description: '把岗位差距转成可执行的准备路线' }
  }
  return allItems.find((item) => route.path.startsWith(item.path)) ?? overviewItem
})

watch(
  () => route.path,
  async () => {
    sidebarOpen.value = false
    await nextTick()
    mainContent.value?.focus({ preventScroll: true })
  },
)

watch(showGuestLogoutConfirm, async (open) => {
  if (!open) return
  await nextTick()
  guestDialog.value?.querySelector<HTMLElement>('[data-testid="guest-register-action"]')?.focus()
})

function trapDialogFocus(event: KeyboardEvent) {
  if (event.key !== 'Tab' || !guestDialog.value) return
  const focusable = Array.from(guestDialog.value.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

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

function goToGuestRegistration() {
  showGuestLogoutConfirm.value = false
  router.push('/login?mode=register&guest=1')
}
</script>

<template>
  <div class="flex min-h-screen bg-[var(--bg)]">
    <a
      href="#main-content"
      class="focus-ring fixed left-4 top-3 z-[300] -translate-y-20 rounded-[var(--radius-sm)] bg-[var(--text-primary)] px-4 py-2 text-sm text-[var(--bg)] transition-transform focus:translate-y-0"
    >
      跳到主要内容
    </a>

    <Transition name="fade">
      <button
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-black/50 lg:hidden"
        aria-label="关闭导航"
        @click="sidebarOpen = false"
      />
    </Transition>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-[var(--border)] bg-[var(--surface)] transition-transform duration-200 lg:static lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      aria-label="桌面端主导航"
    >
      <div class="flex items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-5">
        <RouterLink to="/dashboard" class="focus-ring flex items-center gap-3 rounded-[var(--radius-sm)]">
          <span class="grid size-10 place-items-center rounded-[var(--radius-sm)] bg-[var(--text-primary)] text-xs font-bold tracking-[0.14em] text-[var(--bg)]">
            IP
          </span>
          <span>
            <span class="font-display block text-base font-semibold">InterviewPilot</span>
            <span class="block text-xs text-[var(--text-muted)]">面试准备工作台</span>
          </span>
        </RouterLink>
        <Button variant="ghost" size="icon" class="lg:hidden" aria-label="关闭导航" @click="sidebarOpen = false">
          <X class="size-5" />
        </Button>
      </div>

      <nav class="flex flex-1 flex-col overflow-y-auto px-3 py-5">
        <RouterLink
          :to="overviewItem.path"
          class="focus-ring flex min-h-11 items-center gap-3 rounded-[var(--radius-md)] px-3 text-sm font-semibold transition-colors"
          :class="route.path.startsWith(overviewItem.path)
            ? 'bg-[var(--text-primary)] text-[var(--bg)]'
            : 'text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--text-primary)]'"
        >
          <Gauge class="size-4.5" />
          概览
        </RouterLink>

        <div v-for="group in navGroups" :key="group.label" class="mt-6">
          <p class="mb-2 px-3 text-[11px] font-bold tracking-[0.16em] text-[var(--text-muted)]">
            {{ group.label }}
          </p>
          <div class="flex flex-col gap-1">
            <RouterLink
              v-for="item in group.items"
              :key="item.path"
              :to="item.path"
              class="focus-ring flex min-h-11 items-center gap-3 rounded-[var(--radius-md)] px-3 text-sm font-medium transition-colors"
              :class="route.path.startsWith(item.path)
                ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--text-primary)]'"
            >
              <component :is="item.icon" class="size-4.5" />
              {{ item.label }}
            </RouterLink>
          </div>
        </div>
      </nav>

      <div class="border-t border-[var(--border)] p-3">
        <RouterLink
          to="/settings"
          class="focus-ring mb-2 flex min-h-11 items-center gap-3 rounded-[var(--radius-md)] px-3 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:bg-[var(--surface-muted)]"
        >
          <Settings class="size-4.5" />
          设置
        </RouterLink>
        <div class="rounded-[var(--radius-md)] bg-[var(--surface-muted)] p-3">
          <div class="flex items-center gap-3">
            <UserCircle class="size-8 shrink-0 text-[var(--text-secondary)]" />
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold">{{ auth.user?.name }}</p>
              <p class="truncate text-xs text-[var(--text-muted)]">{{ auth.user?.username }}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" class="mt-2 w-full justify-start" @click="logout">
            <LogOut class="size-4" />
            退出登录
          </Button>
        </div>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <div
        v-if="auth.isGuest"
        class="flex flex-wrap items-center justify-center gap-2 border-b border-[var(--warning)]/30 bg-[var(--warning-light)] px-4 py-2 text-sm"
      >
        <AlertTriangle class="size-4 text-[var(--warning)]" />
        <span class="text-[var(--text-secondary)]">游客数据仅在本次会话中保存</span>
        <Button variant="ghost" size="sm" @click="goToGuestRegistration">注册正式账号</Button>
      </div>

      <header class="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--bg)]/95">
        <div class="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <div class="flex min-w-0 items-center gap-3">
            <Button variant="ghost" size="icon" class="shrink-0 lg:hidden" aria-label="打开导航" @click="sidebarOpen = true">
              <Menu class="size-5" />
            </Button>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-semibold">{{ currentPage.label }}</h1>
              <p class="hidden truncate text-xs text-[var(--text-muted)] sm:block">{{ currentPage.description }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <ThemeToggle />
            <Button
              data-testid="coach-entry"
              variant="secondary"
              size="sm"
              @click="router.push('/assistant')"
            >
              <MessageCircleQuestion class="size-4" />
              <span class="hidden sm:inline">问教练</span>
            </Button>
            <Button size="sm" class="hidden md:inline-flex" @click="router.push('/interview')">
              开始练习
            </Button>
          </div>
        </div>
      </header>

      <main
        id="main-content"
        ref="mainContent"
        tabindex="-1"
        class="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 outline-none sm:px-6 lg:px-8 lg:py-8"
      >
        <RouterView />
      </main>

      <nav
        aria-label="移动端主导航"
        class="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--border)] bg-[var(--surface)] pb-[env(safe-area-inset-bottom)] lg:hidden"
      >
        <div class="grid grid-cols-5 px-1 py-1.5">
          <RouterLink
            v-for="item in mobileNavItems"
            :key="item.path"
            :to="item.path"
            class="focus-ring flex min-h-12 flex-col items-center justify-center gap-0.5 rounded-[var(--radius-sm)] px-1 text-[10px] font-semibold transition-colors"
            :class="route.path.startsWith(item.path) ? 'text-[var(--primary)]' : 'text-[var(--text-muted)]'"
          >
            <component :is="item.icon" class="size-5" />
            {{ item.shortLabel ?? item.label }}
          </RouterLink>
        </div>
      </nav>
      <div class="h-20 lg:hidden" />
    </div>

    <ToastContainer />

    <Transition name="fade">
      <div
        v-if="showGuestLogoutConfirm"
        ref="guestDialog"
        class="fixed inset-0 z-[100] grid place-items-center bg-black/55 p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guest-logout-title"
        tabindex="-1"
        @click.self="showGuestLogoutConfirm = false"
        @keydown.esc="showGuestLogoutConfirm = false"
        @keydown.tab="trapDialogFocus"
      >
        <div class="surface-raised w-full max-w-sm rounded-[var(--radius-lg)] p-6">
          <div class="mb-4 flex items-start gap-3">
            <span class="grid size-10 shrink-0 place-items-center rounded-full bg-[var(--warning-light)]">
              <AlertTriangle class="size-5 text-[var(--warning)]" />
            </span>
            <div>
              <h2 id="guest-logout-title" class="text-lg font-semibold">确认退出游客模式？</h2>
              <p class="mt-1 text-sm text-[var(--text-secondary)]">未注册的数据将在 24 小时后清除。</p>
            </div>
          </div>
          <div class="flex flex-col gap-2 sm:flex-row">
            <Button data-testid="guest-register-action" class="flex-1" @click="goToGuestRegistration">注册正式账号</Button>
            <Button variant="secondary" class="flex-1" @click="confirmGuestLogout">仍然退出</Button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-fast) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
