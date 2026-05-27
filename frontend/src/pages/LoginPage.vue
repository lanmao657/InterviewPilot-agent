<!-- frontend/src/pages/LoginPage.vue -->
<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const form = ref({ username: 'demo', password: 'password123' })
const usernameRequirements = '3-120 个字符，不能含 @'
const passwordRequirements = '至少 8 位'

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
    const session = isRegister.value ? await api.register(form.value) : await api.login(form.value)
    auth.setSession(session)
    router.push('/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="relative grid min-h-screen place-items-center overflow-hidden px-4 py-10">
    <!-- 背景装饰 -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-[var(--primary)]/10 blur-3xl" />
      <div class="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-[var(--accent)]/10 blur-3xl" />
    </div>

    <!-- 主题切换 -->
    <div class="absolute right-4 top-4">
      <ThemeToggle />
    </div>

    <!-- 登录卡片 -->
    <div class="glass-elevated w-full max-w-md rounded-2xl p-8 animate-fade-in-up">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 grid size-16 place-items-center rounded-2xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-2xl font-bold text-white shadow-lg">
          IP
        </div>
        <h1 class="text-2xl font-bold">InterviewPilot</h1>
        <p class="mt-1 text-sm text-[var(--text-secondary)]">AI 面试准备平台</p>
      </div>

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
        <p v-if="error" class="rounded-xl border border-[var(--error)]/30 bg-[var(--error)]/10 px-4 py-2.5 text-sm text-[var(--error)]">
          {{ error }}
        </p>
        <Button type="submit" :disabled="loading" class="mt-2">
          <Loader2 v-if="loading" class="size-4 animate-spin" />
          {{ isRegister ? '注册并进入' : '登录' }}
        </Button>
        <Button type="button" variant="ghost" @click="toggleRegister">
          {{ isRegister ? '已有账号，去登录' : '没有账号，创建一个' }}
        </Button>
      </form>
    </div>
  </main>
</template>
