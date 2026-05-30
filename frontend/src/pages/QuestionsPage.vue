<!-- frontend/src/pages/QuestionsPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { CreditCard, RefreshCw, X } from 'lucide-vue-next'
import { ref } from 'vue'

import AnswerCard from '@/components/AnswerCard.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

const queryClient = useQueryClient()
const focus = ref('项目深挖与 STAR 表达')
const count = ref(6)
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })

// 话术卡片状态
const answerCards = ref<Array<Record<string, unknown>>>([])
const showCards = ref(false)

const generateMutation = useMutation({
  mutationFn: () =>
    api.generateQuestions({
      prep_plan_id: plansQuery.data.value?.[0]?.id,
      count: count.value,
      focus: focus.value,
    }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['questions'] }),
})

const cardMutation = useMutation({
  mutationFn: () => api.answerCards(),
  onSuccess: (data) => {
    answerCards.value = data
    showCards.value = true
  },
})

// 难度与 Badge 变体映射
const difficultyVariant: Record<string, 'default' | 'accent' | 'warning'> = {
  easy: 'default',
  medium: 'accent',
  hard: 'warning',
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <!-- 生成配置 -->
    <div class="glass rounded-2xl p-6">
      <h2 class="text-lg font-semibold">题库生成</h2>
      <p class="mb-5 text-sm text-[var(--text-secondary)]">根据准备计划生成结构化面试题</p>

      <div class="grid gap-4 md:grid-cols-[1fr_160px_auto]">
        <label class="flex flex-col gap-2 text-sm font-medium">
          训练重点
          <Input v-model="focus" />
        </label>
        <label class="flex flex-col gap-2 text-sm font-medium">
          题目数量
          <Input v-model.number="count" type="number" min="1" max="12" />
        </label>
        <div class="flex gap-2 self-end">
          <Button :disabled="generateMutation.isPending.value" @click="generateMutation.mutate()">
            <RefreshCw class="size-4" :class="{ 'animate-spin': generateMutation.isPending.value }" />
            生成题目
          </Button>
          <Button
            variant="secondary"
            :disabled="!questionsQuery.data.value?.length || cardMutation.isPending.value"
            @click="cardMutation.mutate()"
          >
            <CreditCard class="size-4" />
            话术卡片
          </Button>
        </div>
      </div>
    </div>

    <!-- 话术卡片展示 -->
    <Transition name="page">
      <section v-if="showCards" class="glass rounded-2xl p-6">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold">STAR 话术卡片</h3>
            <p class="text-xs text-[var(--text-muted)]">每道题的参考回答框架和关键词提示</p>
          </div>
          <Button variant="ghost" size="icon" @click="showCards = false">
            <X class="size-4" />
          </Button>
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <AnswerCard :cards="(answerCards as any)" />
        </div>
      </section>
    </Transition>

    <!-- 题目列表 -->
    <section class="grid gap-4 lg:grid-cols-2">
      <div
        v-for="(question, index) in questionsQuery.data.value"
        :key="question.id"
        class="glass rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg animate-stagger"
        :style="{ '--stagger-index': index }"
      >
        <div class="mb-3 flex items-center justify-between gap-3">
          <Badge variant="accent">{{ question.category }}</Badge>
          <Badge :variant="difficultyVariant[question.difficulty] ?? 'default'">{{ question.difficulty }}</Badge>
        </div>
        <p class="text-base font-medium leading-6">{{ question.prompt }}</p>
        <p class="mt-3 text-xs text-[var(--text-muted)]">评分维度：清晰度、结构、证据、复盘深度</p>
      </div>
    </section>
    <p v-if="!questionsQuery.data.value?.length" class="text-sm text-[var(--text-muted)]">还没有题目，先生成一组。</p>
  </div>
</template>
