<!-- frontend/src/pages/PlanDetailPage.vue -->
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Flag,
  Layers,
  Lightbulb,
  Rocket,
  ShieldAlert,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Zap,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

const route = useRoute()
const router = useRouter()
const planId = computed(() => Number(route.params.id))

const planQuery = useQuery({
  queryKey: ['plan', planId],
  queryFn: () => api.getPlan(planId.value),
  enabled: computed(() => !!planId.value),
})

const plan = computed(() => planQuery.data.value)
const roadmap = computed(() => plan.value?.roadmap ?? ({} as Record<string, unknown>))
const summary = computed(() => roadmap.value.summary as string ?? '')
const milestones = computed(() => roadmap.value.milestones as string[] ?? [])
const focusAreas = computed(() => roadmap.value.focusAreas as string[] ?? [])
const strengths = computed(() => roadmap.value.strengths as string[] ?? [])
const gaps = computed(() => roadmap.value.gaps as string[] ?? [])
const keywords = computed(() => roadmap.value.keywords as Array<{ keyword: string; importance?: string }> ?? [])
const fitScore = computed(() => plan.value?.fit_score ?? 0)

const fitLevel = computed(() => {
  const s = fitScore.value
  if (s >= 85) return { label: '高度匹配', color: 'var(--success)', icon: Sparkles }
  if (s >= 70) return { label: '较好匹配', color: 'var(--primary)', icon: TrendingUp }
  if (s >= 50) return { label: '部分匹配', color: 'var(--warning)', icon: Flag }
  return { label: '差距较大', color: 'var(--error)', icon: ShieldAlert }
})

const milestoneIcons = [Target, BookOpen, Zap, Rocket]

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <!-- 返回导航 + 标题区 -->
    <div class="flex flex-col gap-4 border-b border-[var(--border)] pb-6 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <Button variant="ghost" size="sm" @click="router.back()">
          <ArrowLeft class="size-4" />
        </Button>
        <div>
          <p class="eyebrow">准备路线</p>
          <h2 class="mt-1 text-2xl font-semibold">{{ plan?.title ?? '准备计划' }}</h2>
          <p class="text-sm text-[var(--text-muted)]">
            {{ plan?.target_role }} · {{ plan ? formatDate(plan.created_at) : '' }}
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button variant="secondary" size="sm" @click="router.push('/questions')">
          生成针对性题目
          <ArrowRight class="size-3" />
        </Button>
        <Button size="sm" @click="router.push('/interview')">
          开始模拟面试
          <ArrowRight class="size-3" />
        </Button>
      </div>
    </div>

    <section class="surface-raised grid overflow-hidden rounded-[var(--radius-lg)] sm:grid-cols-[180px_1fr]">
      <div class="flex flex-col justify-center bg-[var(--surface-muted)] p-6 sm:border-r sm:border-[var(--border)] sm:p-8">
        <span class="font-mono text-5xl font-semibold tabular-nums">{{ fitScore }}</span>
        <span class="mt-1 text-xs font-bold tracking-[0.12em] text-[var(--text-muted)]">岗位匹配度 / 100</span>
        <Badge :style="{ borderColor: fitLevel.color, color: fitLevel.color }" variant="outline" class="mt-4 self-start">
          <component :is="fitLevel.icon" class="size-3" />
          {{ fitLevel.label }}
        </Badge>
      </div>
      <div class="p-6 sm:p-8">
        <div class="mb-3 flex items-center gap-2">
          <Lightbulb class="size-4 text-[var(--primary)]" />
          <h3 class="text-lg font-semibold">岗位匹配结论</h3>
        </div>
        <p class="max-w-3xl text-sm leading-7 text-[var(--text-secondary)]">{{ summary || '暂无分析' }}</p>
        <Progress :value="fitScore" class="mt-5" />
      </div>
    </section>

    <!-- 准备路线（里程碑） -->
    <section class="surface rounded-[var(--radius-lg)] p-6 sm:p-8">
      <div class="mb-5 flex items-center gap-2">
        <Layers class="size-5 text-[var(--primary)]" />
        <h2 class="text-lg font-semibold">准备路线</h2>
        <span class="text-xs text-[var(--text-muted)]">{{ milestones.length }} 个阶段</span>
      </div>

      <!-- 竖向时间线 -->
      <div class="timeline">
        <div
          v-for="(step, i) in milestones"
          :key="i"
          class="timeline__item"
        >
          <div class="timeline__connector">
            <div class="timeline__dot" :class="{ 'timeline__dot--active': i === 0 }">
              <component :is="milestoneIcons[i] ?? Flag" class="size-4" />
            </div>
            <div v-if="i < milestones.length - 1" class="timeline__line" />
          </div>
          <div class="timeline__content">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-[var(--primary)]">
              阶段 {{ i + 1 }}
            </span>
            <p class="mt-1 text-sm font-medium leading-5">{{ step }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 焦点 + 优势 + 差距 三栏 -->
    <div class="grid gap-4 lg:grid-cols-3">
      <!-- 重点方向 -->
      <section class="surface rounded-[var(--radius-lg)] p-5">
        <div class="mb-4 flex items-center gap-2">
          <Target class="size-4 text-[var(--primary)]" />
          <h3 class="text-sm font-semibold">重点方向</h3>
        </div>
        <div class="flex flex-col gap-2.5">
          <div
            v-for="(area, i) in focusAreas"
            :key="i"
            class="focus-card rounded-[var(--radius-md)] border border-[var(--border)] p-3"
          >
            <div class="flex items-center gap-2">
              <span
                class="flex size-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                :style="{ background: `var(--primary)` }"
              >
                {{ i + 1 }}
              </span>
              <p class="text-sm">{{ area }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 你的优势 -->
      <section class="surface rounded-[var(--radius-lg)] p-5">
        <div class="mb-4 flex items-center gap-2">
          <Star class="size-4 text-[var(--success)]" />
          <h3 class="text-sm font-semibold">你的优势</h3>
        </div>
        <div v-if="strengths.length" class="flex flex-col gap-2.5">
          <div
            v-for="(s, i) in strengths"
            :key="i"
            class="strength-card rounded-[var(--radius-md)] border border-[var(--border)] p-3"
          >
            <div class="flex items-start gap-2">
              <CheckCircle2 class="mt-0.5 size-4 shrink-0 text-[var(--success)]" />
              <p class="text-sm">{{ s }}</p>
            </div>
          </div>
        </div>
        <p v-else class="text-xs text-[var(--text-muted)]">上传简历后可自动分析优势</p>
      </section>

      <!-- 差距 / 待提升 -->
      <section class="surface rounded-[var(--radius-lg)] p-5">
        <div class="mb-4 flex items-center gap-2">
          <ShieldAlert class="size-4 text-[var(--warning)]" />
          <h3 class="text-sm font-semibold">待提升</h3>
        </div>
        <div v-if="gaps.length" class="flex flex-col gap-2.5">
          <div
            v-for="(g, i) in gaps"
            :key="i"
            class="gap-card rounded-[var(--radius-md)] border border-[var(--border)] p-3"
          >
            <div class="flex items-start gap-2">
              <ChevronRight class="mt-0.5 size-4 shrink-0 text-[var(--warning)]" />
              <p class="text-sm">{{ g }}</p>
            </div>
          </div>
        </div>
        <p v-else class="text-xs text-[var(--text-muted)]">暂无差距分析</p>
      </section>
    </div>

    <!-- 关键词标签云 -->
    <section v-if="keywords.length" class="surface rounded-[var(--radius-lg)] p-6">
      <div class="mb-4 flex items-center gap-2">
        <BookOpen class="size-5 text-[var(--primary)]" />
        <h2 class="text-lg font-semibold">岗位关键词</h2>
        <span class="text-xs text-[var(--text-muted)]">{{ keywords.length }} 个</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(kw, i) in keywords"
          :key="i"
          class="keyword-pill"
          :class="{ 'keyword-pill--high': kw.importance === 'high' }"
        >
          {{ kw.keyword }}
        </span>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ─── 环形进度 ─── */
.score-ring {
  --size: 120px;
  --stroke: 10;
  --pct: calc(var(--score) / 100);
  --circumference: calc(2 * 3.14159 * (50 - var(--stroke)));
  --offset: calc(var(--circumference) * (1 - var(--pct)));

  position: relative;
  width: var(--size);
  height: var(--size);
}

.score-ring::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(
    var(--ring-color) calc(var(--score) * 3.6deg),
    var(--bg-input) 0deg
  );
  mask: radial-gradient(circle, transparent calc(50% - var(--stroke) * 1px - 1px), #000 calc(50% - var(--stroke) * 1px));
  -webkit-mask: radial-gradient(circle, transparent calc(50% - var(--stroke) * 1px - 1px), #000 calc(50% - var(--stroke) * 1px));
  opacity: 0.2;
}

.score-ring::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(
    var(--ring-color) calc(var(--score) * 3.6deg),
    transparent 0deg
  );
  mask: radial-gradient(circle, transparent calc(50% - var(--stroke) * 1px - 1px), #000 calc(50% - var(--stroke) * 1px));
  -webkit-mask: radial-gradient(circle, transparent calc(50% - var(--stroke) * 1px - 1px), #000 calc(50% - var(--stroke) * 1px));
}

.score-ring__value,
.score-ring__label {
  position: relative;
  z-index: 1;
  display: block;
  text-align: center;
}

.score-ring__value {
  padding-top: 30px;
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.05em;
  color: var(--text-primary);
  line-height: 1;
}

.score-ring__label {
  margin-top: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* ─── 时间线 ─── */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline__item {
  display: flex;
  gap: 1rem;
}

.timeline__connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timeline__dot {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--bg-input);
  color: var(--text-muted);
  border: 2px solid var(--border, rgba(128, 128, 128, 0.2));
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.timeline__dot--active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--primary) 20%, transparent);
}

.timeline__line {
  width: 2px;
  flex: 1;
  min-height: 1.5rem;
  background: linear-gradient(
    to bottom,
    color-mix(in srgb, var(--primary) 40%, transparent),
    var(--bg-input)
  );
  margin: 0.25rem 0;
}

.timeline__content {
  padding: 0.25rem 0 1.5rem;
}

.focus-card:hover {
  border-color: var(--primary);
  transition: border-color var(--duration-fast) ease;
}

.strength-card:hover {
  border-color: var(--success);
  transition: border-color 0.2s ease;
}

.gap-card:hover {
  border-color: var(--warning);
  transition: border-color 0.2s ease;
}

/* ─── 关键词标签 ─── */
.keyword-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--bg-input);
  color: var(--text-secondary);
  border: 1px solid transparent;
  transition: border-color var(--duration-fast) ease, color var(--duration-fast) ease;
}

.keyword-pill:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 8%, transparent);
}

.keyword-pill--high {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--primary);
  font-weight: 600;
}
</style>
