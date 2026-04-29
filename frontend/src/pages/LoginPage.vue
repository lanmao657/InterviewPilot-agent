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
const form = ref({ name: '候选人', email: 'demo@example.com', password: 'password123' })

async function submit() {
  loading.value = true
  error.value = ''
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
          <label v-if="isRegister" class="flex flex-col gap-2 text-sm font-medium">
            姓名
            <Input v-model="form.name" autocomplete="name" />
          </label>
          <label class="flex flex-col gap-2 text-sm font-medium">
            邮箱
            <Input v-model="form.email" type="email" autocomplete="email" />
          </label>
          <label class="flex flex-col gap-2 text-sm font-medium">
            密码
            <Input v-model="form.password" type="password" autocomplete="current-password" />
          </label>
          <p v-if="error" class="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {{ error }}
          </p>
          <Button type="submit" :disabled="loading">
            <Loader2 v-if="loading" class="animate-spin" data-icon="inline-start" />
            {{ isRegister ? '注册并进入' : '登录' }}
          </Button>
          <Button type="button" variant="ghost" @click="isRegister = !isRegister">
            {{ isRegister ? '已有账号，去登录' : '没有账号，创建一个' }}
          </Button>
        </form>
      </CardContent>
    </Card>
  </main>
</template>
