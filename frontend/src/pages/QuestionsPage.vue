<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { CreditCard, Filter, RefreshCw, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import AnswerCard from '@/components/AnswerCard.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

const queryClient = useQueryClient()
const focus = ref('项目深挖与 STAR 表达')
const count = ref(6)
const message = ref('')
const difficultyFilter = ref('all')
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const answerCards = ref<Array<Record<string, unknown>>>([])
const showCards = ref(false)

const filteredQuestions = computed(() => {
  const questions = questionsQuery.data.value ?? []
  if (difficultyFilter.value === 'all') return questions
  return questions.filter((question) => question.difficulty === difficultyFilter.value)
})

const generateMutation = useMutation({
  mutationFn: async () => {
    message.value = ''
    return api.generateQuestions({
      prep_plan_id: plansQuery.data.value?.[0]?.id,
      count: count.value,
      focus: focus.value,
    })
  },
  onSuccess: (data) => {
    const notice = data.find((question) => typeof question.rubric?._ai_notice === 'string')?.rubric._ai_notice
    message.value = typeof notice === 'string' ? notice : '题目已生成，可以开始筛选和练习'
    queryClient.invalidateQueries({ queryKey: ['questions'] })
  },
  onError: (err: Error) => {
    message.value = `生成失败：${err.message}`
  },
})

const cardMutation = useMutation({
  mutationFn: async () => {
    message.value = ''
    return api.answerCards()
  },
  onSuccess: (data) => {
    answerCards.value = data
    showCards.value = true
  },
  onError: (err: Error) => {
    message.value = `话术卡片生成失败：${err.message}`
  },
})

const difficultyVariant: Record<string, 'default' | 'accent' | 'warning'> = {
  easy: 'default',
  medium: 'accent',
  hard: 'warning',
}
const difficultyLabel: Record<string, string> = { easy: '基础', medium: '进阶', hard: '挑战' }
</script>

<template>
  <div class="flex flex-col gap-8">
    <section class="surface rounded-[var(--radius-lg)] p-6 sm:p-8">
      <div class="mb-6 max-w-2xl">
        <p class="eyebrow">训练准备</p>
        <h2 class="mt-2 text-2xl font-semibold">生成针对性题目</h2>
        <p class="mt-2 text-sm leading-6 text-[var(--text-secondary)]">训练重点越具体，生成的问题越容易检验真实准备程度。</p>
      </div>

      <div class="grid gap-4 lg:grid-cols-[1fr_150px_auto]">
        <label class="flex flex-col gap-2 text-sm font-semibold">
          训练重点
          <Input v-model="focus" />
        </label>
        <label class="flex flex-col gap-2 text-sm font-semibold">
          题目数量
          <Input v-model.number="count" type="number" min="1" max="12" />
        </label>
        <div class="flex flex-wrap gap-2 self-end">
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
            回答提纲
          </Button>
        </div>
      </div>
      <p
        v-if="message"
        class="mt-4 rounded-[var(--radius-sm)] border px-3 py-2 text-sm"
        :class="message.includes('失败')
          ? 'border-[var(--error)]/30 bg-[var(--error-light)] text-[var(--error)]'
          : 'border-[var(--info)]/30 bg-[var(--info-light)] text-[var(--info)]'"
        role="status"
      >
        {{ message }}
      </p>
    </section>

    <section v-if="showCards" class="surface-raised rounded-[var(--radius-lg)] p-6">
      <div class="mb-5 flex items-start justify-between gap-4 border-b border-[var(--border)] pb-4">
        <div>
          <p class="eyebrow">回答准备</p>
          <h2 class="mt-2 text-xl font-semibold">STAR 回答提纲</h2>
          <p class="mt-1 text-sm text-[var(--text-secondary)]">把提纲当作证据清单，不要逐字背诵。</p>
        </div>
        <Button variant="ghost" size="icon" aria-label="关闭回答提纲" @click="showCards = false">
          <X class="size-4" />
        </Button>
      </div>
      <AnswerCard :cards="(answerCards as any)" />
    </section>

    <section>
      <div class="mb-5 flex flex-col gap-3 border-b border-[var(--border)] pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="eyebrow">训练题库</p>
          <h2 class="mt-2 text-2xl font-semibold">{{ questionsQuery.data.value?.length ?? 0 }} 道题目</h2>
        </div>
        <label class="flex items-center gap-2 text-sm font-semibold">
          <Filter class="size-4 text-[var(--text-muted)]" />
          <span class="sr-only">按难度筛选</span>
          <select
            v-model="difficultyFilter"
            data-testid="difficulty-filter"
            class="h-11 rounded-[var(--radius-md)] border border-[var(--border-strong)] bg-[var(--bg-input)] px-3 text-sm focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20"
          >
            <option value="all">全部难度</option>
            <option value="easy">基础</option>
            <option value="medium">进阶</option>
            <option value="hard">挑战</option>
          </select>
        </label>
      </div>

      <ol v-if="filteredQuestions.length" class="grid gap-4 lg:grid-cols-2">
        <li
          v-for="(question, index) in filteredQuestions"
          :key="question.id"
          class="surface rounded-[var(--radius-lg)] p-5 sm:p-6"
        >
          <div class="mb-4 flex items-center justify-between gap-3">
            <span class="font-mono text-xs text-[var(--text-muted)]">{{ String(index + 1).padStart(2, '0') }}</span>
            <div class="flex gap-2">
              <Badge variant="outline">{{ question.category }}</Badge>
              <Badge :variant="difficultyVariant[question.difficulty] ?? 'default'">
                {{ difficultyLabel[question.difficulty] ?? question.difficulty }}
              </Badge>
            </div>
          </div>
          <p class="text-base font-semibold leading-7">{{ question.prompt }}</p>
          <p class="mt-4 border-t border-[var(--border)] pt-3 text-xs text-[var(--text-muted)]">观察：表达清晰、结构完整、证据具体、复盘深入</p>
        </li>
      </ol>
      <div v-else class="surface-muted rounded-[var(--radius-lg)] p-8 text-center">
        <h3 class="text-lg font-semibold">{{ questionsQuery.data.value?.length ? '没有符合筛选条件的题目' : '还没有训练题目' }}</h3>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">{{ questionsQuery.data.value?.length ? '切换难度查看其他题目。' : '先从一个具体训练重点生成题目。' }}</p>
      </div>
    </section>
  </div>
</template>
