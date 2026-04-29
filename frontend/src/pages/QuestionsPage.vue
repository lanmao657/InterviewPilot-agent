<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { RefreshCw } from 'lucide-vue-next'
import { ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

const queryClient = useQueryClient()
const focus = ref('项目深挖与 STAR 表达')
const count = ref(6)
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })

const generateMutation = useMutation({
  mutationFn: () =>
    api.generateQuestions({
      prep_plan_id: plansQuery.data.value?.[0]?.id,
      count: count.value,
      focus: focus.value,
    }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['questions'] }),
})
</script>

<template>
  <div class="flex flex-col gap-5">
    <Card>
      <CardHeader>
        <CardTitle>题库生成</CardTitle>
        <CardDescription>根据准备计划生成结构化面试题。</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4 md:grid-cols-[1fr_160px_auto]">
        <label class="flex flex-col gap-2 text-sm font-medium">
          训练重点
          <Input v-model="focus" />
        </label>
        <label class="flex flex-col gap-2 text-sm font-medium">
          题目数量
          <Input v-model.number="count" type="number" min="1" max="12" />
        </label>
        <Button class="self-end" :disabled="generateMutation.isPending.value" @click="generateMutation.mutate()">
          <RefreshCw data-icon="inline-start" />
          生成题目
        </Button>
      </CardContent>
    </Card>

    <section class="grid gap-4 lg:grid-cols-2">
      <Card v-for="question in questionsQuery.data.value" :key="question.id">
        <CardHeader>
          <div class="flex items-center justify-between gap-3">
            <Badge variant="accent">{{ question.category }}</Badge>
            <Badge variant="outline">{{ question.difficulty }}</Badge>
          </div>
          <CardTitle class="leading-6">{{ question.prompt }}</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground">评分维度：清晰度、结构、证据、复盘深度。</p>
        </CardContent>
      </Card>
    </section>
    <p v-if="!questionsQuery.data.value?.length" class="text-sm text-muted-foreground">还没有题目，先生成一组。</p>
  </div>
</template>
