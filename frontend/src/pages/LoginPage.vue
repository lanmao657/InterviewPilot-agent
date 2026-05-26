<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
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
  <main class="grid min-h-screen place-items-center px-4 py-10">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle class="text-2xl">InterviewPilot</CardTitle>
        <CardDescription>登录后开始你的 AI 面试准备闭环。</CardDescription>
      </CardHeader>
      <CardContent>
        <form class="flex flex-col gap-4" @submit.prevent="submit">
          <label class="flex flex-col gap-2 text-sm font-medium">
            {{ isRegister ? '用户名' : '用户名或邮箱' }}
            <Input v-model="form.username" autocomplete="username" />
            <span v-if="isRegister" class="text-[11px] font-normal leading-4 text-muted-foreground/70">
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
            <span v-if="isRegister" class="text-[11px] font-normal leading-4 text-muted-foreground/70">
              {{ passwordRequirements }}
            </span>
          </label>
          <p v-if="error" class="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {{ error }}
          </p>
          <Button type="submit" :disabled="loading">
            <Loader2 v-if="loading" class="animate-spin" data-icon="inline-start" />
            {{ isRegister ? '注册并进入' : '登录' }}
          </Button>
          <Button type="button" variant="ghost" @click="toggleRegister">
            {{ isRegister ? '已有账号，去登录' : '没有账号，创建一个' }}
          </Button>
        </form>
      </CardContent>
    </Card>
  </main>
</template>
