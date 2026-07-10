<!-- frontend/src/pages/LoginPage.vue -->
<script setup lang="ts">
import { Loader2, UserX } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const isRegister = ref(route.query.mode === 'register')
const loading = ref(false)
const guestLoading = ref(false)
const error = ref('')
const form = ref({ username: 'demo', password: 'password123' })
const usernameRequirements = '3-120 个字符，不能含 @'
const passwordRequirements = '至少 8 位'
const isGuestConversion = computed(() => isRegister.value && route.query.guest === '1' && auth.isGuest)

function validateRegistrationForm() {
  const username = form.value.username.trim()
  if (!username) return '用户名不合规范：用户名不能为空'
  if (username.length < 3) return '用户名不合规范：用户名至少需要 3 个字符'
  if (username.length > 120) return '用户名不合规范：用户名最多 120 个字符'
  if (username.includes('@')) return '用户名不合规范：不能使用邮箱格式'
  if (!form.value.password) return '密码不合规范：密码不能为空'
  if (form.value.password.length < 8) return '密码不合规范：密码至少需要 8 个字符'
  return ''
}

function toggleRegister() {
  isRegister.value = !isRegister.value
  error.value = ''
}

async function submit() {
  error.value = ''
  if (isRegister.value) {
    const validationError = validateRegistrationForm()
    if (validationError) {
      error.value = validationError
      return
    }
  }
  loading.value = true
  try {
    const session = isGuestConversion.value
      ? await api.convertGuest(form.value)
      : isRegister.value
        ? await api.register(form.value)
        : await api.login(form.value)
    auth.setSession(session, session.user.is_anonymous)
    router.push('/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}

async function guestLogin() {
  guestLoading.value = true
  error.value = ''
  try {
    const session = await api.guestLogin()
    auth.setSession(session, true)  // isGuest = true
    router.push('/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '游客登录失败'
  } finally {
    guestLoading.value = false
  }
}
</script>

<template>
  <main class="relative min-h-screen bg-[var(--bg)] px-4 py-8 sm:px-8 lg:grid lg:grid-cols-[1.05fr_0.95fr] lg:items-stretch lg:p-0">
    <div class="absolute right-4 top-4">
      <ThemeToggle />
    </div>

    <section class="mx-auto flex min-h-[42vh] max-w-2xl flex-col justify-between py-16 lg:min-h-screen lg:max-w-none lg:border-r lg:border-[var(--border)] lg:px-[10vw] lg:py-20">
      <div class="flex items-center gap-3">
        <span class="grid size-11 place-items-center rounded-[var(--radius-sm)] bg-[var(--text-primary)] text-xs font-bold tracking-[0.14em] text-[var(--bg)]">IP</span>
        <div>
          <p class="font-display text-lg font-semibold">InterviewPilot</p>
          <p class="text-xs text-[var(--text-muted)]">面试准备工作台</p>
        </div>
      </div>

      <div class="max-w-xl py-12">
        <p class="eyebrow">从材料到复盘</p>
        <h1 class="mt-5 text-4xl font-semibold leading-[1.2] sm:text-5xl lg:text-6xl">
          把经历整理成<br class="hidden sm:block">能被听懂的证据。
        </h1>
        <p class="mt-6 max-w-lg text-base leading-8 text-[var(--text-secondary)]">
          围绕目标岗位整理材料、训练回答、复盘表现。每一步都留下可继续改进的依据。
        </p>
      </div>

      <p class="text-xs leading-5 text-[var(--text-muted)]">准备不是背标准答案，而是更准确地讲清楚你做过什么。</p>
    </section>

    <section class="mx-auto flex w-full max-w-md items-center py-10 lg:min-h-screen">
      <div class="surface-raised w-full rounded-[var(--radius-lg)] p-6 sm:p-8">
        <p class="eyebrow">{{ isRegister ? '建立账户' : '欢迎回来' }}</p>
        <h2 class="mt-2 text-2xl font-semibold">{{ isGuestConversion ? '保存游客进度' : isRegister ? '创建账号' : '登录 InterviewPilot' }}</h2>
        <p class="mb-7 mt-2 text-sm text-[var(--text-secondary)]">{{ isRegister ? '保存材料、训练记录与复盘报告。' : '继续上一次面试准备。' }}</p>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <label class="flex flex-col gap-2 text-sm font-medium">
          {{ isRegister ? '用户名' : '用户名或邮箱' }}
          <Input v-model="form.username" autocomplete="username" />
          <span v-if="isRegister" class="text-[11px] font-normal leading-4 text-[var(--text-muted)]">
            {{ usernameRequirements }}
          </span>
        </label>
        <label class="flex flex-col gap-2 text-sm font-medium">
          密码
          <Input
            v-model="form.password"
            type="password"
            :autocomplete="isRegister ? 'new-password' : 'current-password'"
          />
          <span v-if="isRegister" class="text-[11px] font-normal leading-4 text-[var(--text-muted)]">
            {{ passwordRequirements }}
          </span>
        </label>
        <p v-if="error" class="rounded-[var(--radius-md)] border border-[var(--error)]/30 bg-[var(--error-light)] px-4 py-2.5 text-sm text-[var(--error)]" role="alert">
          {{ error }}
        </p>
        <div class="mt-2 flex flex-col gap-2 sm:flex-row">
          <Button type="submit" :disabled="loading" class="flex-1">
            <Loader2 v-if="loading" class="size-4 animate-spin" />
            {{ isGuestConversion ? '注册并保存游客数据' : isRegister ? '注册并进入' : '登录' }}
          </Button>
          <Button type="button" variant="secondary" :disabled="guestLoading" class="flex-1" @click="guestLogin">
            <UserX v-if="!guestLoading" class="size-4" />
            <Loader2 v-else class="size-4 animate-spin" />
            游客体验
          </Button>
        </div>
        <Button type="button" variant="ghost" @click="toggleRegister">
          {{ isRegister ? '已有账号，去登录' : '没有账号，创建一个' }}
        </Button>
      </form>
      </div>
    </section>
  </main>
</template>
