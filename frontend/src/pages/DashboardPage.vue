<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowRight, BadgeCheck, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

const router = useRouter()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const activePlan = computed(() => plansQuery.data.value?.[0])
const fitScore = computed(() => activePlan.value?.fit_score ?? 68)
</script>

<template>
  <div class="flex flex-col gap-5">
    <section class="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader>
          <CardDescription>准备计划</CardDescription>
          <CardTitle class="text-2xl">{{ plansQuery.data.value?.length ?? 0 }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader>
          <CardDescription>资料</CardDescription>
          <CardTitle class="text-2xl">{{ documentsQuery.data.value?.length ?? 0 }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader>
          <CardDescription>题库</CardDescription>
          <CardTitle class="text-2xl">{{ questionsQuery.data.value?.length ?? 0 }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader>
          <CardDescription>报告</CardDescription>
          <CardTitle class="text-2xl">{{ reportsQuery.data.value?.length ?? 0 }}</CardTitle>
        </CardHeader>
      </Card>
    </section>

    <section class="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
      <Card>
        <CardHeader class="flex-row items-start justify-between">
          <div>
            <CardTitle>当前准备计划</CardTitle>
            <CardDescription>{{ activePlan?.target_role ?? '上传简历与 JD 后生成专属路线' }}</CardDescription>
          </div>
          <Badge variant="accent">Fit Score {{ fitScore }}</Badge>
        </CardHeader>
        <CardContent class="flex flex-col gap-5">
          <Progress :value="fitScore" />
          <div class="grid gap-3 md:grid-cols-3">
            <div class="rounded-lg border bg-background/70 p-4">
              <Target class="mb-3 text-primary" />
              <p class="text-sm font-semibold">岗位匹配</p>
              <p class="mt-1 text-sm text-muted-foreground">聚焦 JD 中最高频能力要求。</p>
            </div>
            <div class="rounded-lg border bg-background/70 p-4">
              <MessageSquareText class="mb-3 text-primary" />
              <p class="text-sm font-semibold">模拟追问</p>
              <p class="mt-1 text-sm text-muted-foreground">按回答动态生成追问题。</p>
            </div>
            <div class="rounded-lg border bg-background/70 p-4">
              <BadgeCheck class="mb-3 text-primary" />
              <p class="text-sm font-semibold">STAR Feedback</p>
              <p class="mt-1 text-sm text-muted-foreground">沉淀结构化复盘报告。</p>
            </div>
          </div>
          <Button class="w-fit" @click="router.push('/documents')">
            完善资料
            <ArrowRight data-icon="inline-end" />
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>下一步行动</CardTitle>
          <CardDescription>建议按顺序完成闭环。</CardDescription>
        </CardHeader>
        <CardContent class="flex flex-col gap-3">
          <Button variant="outline" class="justify-start" @click="router.push('/documents')">
            <FileText data-icon="inline-start" />
            上传简历与 JD
          </Button>
          <Button variant="outline" class="justify-start" @click="router.push('/questions')">
            <Target data-icon="inline-start" />
            生成题库
          </Button>
          <Button class="justify-start" @click="router.push('/interview')">
            <MessageSquareText data-icon="inline-start" />
            开始模拟面试
          </Button>
        </CardContent>
      </Card>
    </section>
  </div>
</template>
