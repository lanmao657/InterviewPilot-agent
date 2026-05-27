# 前端 UI 全面重设计实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 InterviewPilot 前端从基础卡片式 UI 重构为玻璃拟态 (Glassmorphism) 风格，支持深色/浅色主题切换、丰富动画和完整移动端适配。

**Architecture:** 在现有 Tailwind CSS 4 + shadcn-vue 组件库基础上，通过 CSS 变量系统实现主题切换，使用 `backdrop-filter` 实现玻璃效果，Vue `<Transition>` 实现页面动画，响应式断点实现移动端适配。不引入新组件库，保留 `reka-ui` + `class-variance-authority` 模式。

**Tech Stack:** Vue 3, TypeScript, Tailwind CSS 4, Vite, shadcn-vue (CVA), reka-ui, lucide-vue-next, ECharts

**Design Spec:** `docs/superpowers/specs/2026-05-27-frontend-ui-redesign.md`

---

## 文件结构映射

### 新增文件
- `frontend/src/composables/useTheme.ts` — 主题切换 composable
- `frontend/src/stores/theme.ts` — 主题状态持久化 store
- `frontend/src/components/ui/glass-card/GlassCard.vue` — 玻璃卡片组件
- `frontend/src/components/ui/glass-card/index.ts` — 导出
- `frontend/src/components/layout/MobileNav.vue` — 移动端底部导航栏
- `frontend/src/components/layout/ThemeToggle.vue` — 主题切换按钮
- `frontend/src/components/ui/skeleton/Skeleton.vue` — 骨架屏组件
- `frontend/src/components/ui/skeleton/index.ts` — 导出

### 修改文件
- `frontend/src/style.css` — 全局样式重构，CSS 变量系统，玻璃效果，动画
- `frontend/src/App.vue` — 添加路由过渡动画，主题 class 绑定
- `frontend/src/components/layout/AppShell.vue` — 侧边栏玻璃效果，Header 重构，移动端适配
- `frontend/src/components/ui/button/Button.vue` — 玻璃风格按钮
- `frontend/src/components/ui/card/Card.vue` — 玻璃风格卡片
- `frontend/src/components/ui/input/Input.vue` — 玻璃风格输入框
- `frontend/src/components/ui/badge/Badge.vue` — 新增变体
- `frontend/src/components/ui/progress/Progress.vue` — 渐变进度条
- `frontend/src/pages/LoginPage.vue` — 全屏玻璃登录页
- `frontend/src/pages/DashboardPage.vue` — 玻璃仪表盘
- `frontend/src/pages/DocumentsPage.vue` — 玻璃文档页
- `frontend/src/pages/QuestionsPage.vue` — 玻璃题库页
- `frontend/src/pages/InterviewPage.vue` — 玻璃面试页
- `frontend/src/pages/ReportsPage.vue` — 玻璃报告页
- `frontend/src/pages/SettingsPage.vue` — 玻璃设置页
- `frontend/src/pages/AssistantPage.vue` — 玻璃助手页
- `frontend/src/components/assistant/GlobalAssistantWidget.vue` — 玻璃风格悬浮窗
- `frontend/src/components/assistant/AssistantChatPanel.vue` — 玻璃风格聊天面板

---

## 阶段一：主题系统与 CSS 基础设施

### Task 1.1: CSS 变量系统与玻璃效果基础

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: 重写 style.css，添加完整的 CSS 变量系统**

```css
@import "tailwindcss";

@theme {
  --font-sans: Inter, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "Fira Code", "JetBrains Mono", monospace;
}

:root {
  /* 背景 */
  --bg-gradient-start: #f0f4f8;
  --bg-gradient-end: #e2e8f0;
  --bg-gradient: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));

  /* 玻璃效果 */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-bg-hover: rgba(255, 255, 255, 0.85);
  --glass-border: rgba(255, 255, 255, 0.3);
  --glass-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.4);
  --glass-shadow-hover: 0 8px 12px -2px rgba(0, 0, 0, 0.15), 0 4px 6px -2px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.4);

  /* 主色调 */
  --primary: #3b82f6;
  --primary-light: #60a5fa;
  --primary-dark: #2563eb;
  --primary-gradient: linear-gradient(135deg, #3b82f6, #2563eb);
  --primary-glow: rgba(59, 130, 246, 0.4);

  /* 强调色 */
  --accent: #8b5cf6;
  --accent-light: #a78bfa;

  /* 文字 */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;

  /* 背景色 */
  --bg: #f0f4f8;
  --bg-card: rgba(255, 255, 255, 0.7);
  --bg-elevated: rgba(255, 255, 255, 0.85);
  --bg-input: rgba(255, 255, 255, 0.5);

  /* 边框 */
  --border: rgba(0, 0, 0, 0.08);
  --border-hover: rgba(59, 130, 246, 0.3);

  /* 状态颜色 */
  --success: #10b981;
  --success-light: rgba(16, 185, 129, 0.1);
  --warning: #f59e0b;
  --warning-light: rgba(245, 158, 11, 0.1);
  --error: #ef4444;
  --error-light: rgba(239, 68, 68, 0.1);
  --info: #3b82f6;
  --info-light: rgba(59, 130, 246, 0.1);

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);

  /* 圆角 */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

.dark {
  --bg-gradient-start: #0f172a;
  --bg-gradient-end: #1e293b;

  --glass-bg: rgba(30, 41, 59, 0.7);
  --glass-bg-hover: rgba(30, 41, 59, 0.85);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  --glass-shadow-hover: 0 8px 12px -2px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);

  --primary: #60a5fa;
  --primary-light: #93c5fd;
  --primary-dark: #3b82f6;
  --primary-glow: rgba(96, 165, 250, 0.3);

  --accent: #a78bfa;
  --accent-light: #c4b5fd;

  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  --bg: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.7);
  --bg-elevated: rgba(30, 41, 59, 0.85);
  --bg-input: rgba(30, 41, 59, 0.5);

  --border: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(96, 165, 250, 0.3);

  --success: #34d399;
  --warning: #fbbf24;
  --error: #f87171;
  --info: #60a5fa;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
}

* {
  border-color: var(--border);
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background: var(--bg-gradient);
  color: var(--text-primary);
  font-family: var(--font-sans);
  transition: background-color 300ms ease, color 300ms ease;
}

button,
input,
textarea {
  font: inherit;
}

.focus-ring {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-ring:focus-visible {
  outline-color: var(--primary);
}

/* 玻璃效果工具类 */
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.glass-elevated {
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(200%);
  -webkit-backdrop-filter: blur(20px) saturate(200%);
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15), 0 4px 6px -4px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.glass-flat {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
}

/* 动画 */
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-out-up {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-8px); }
}

@keyframes slide-in-left {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes slide-out-left {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.animate-fade-in-up {
  animation: fade-in-up 300ms ease-out both;
}

.animate-stagger {
  animation: fade-in-up 300ms ease-out both;
  animation-delay: calc(var(--stagger-index, 0) * 60ms);
}

.skeleton {
  background: linear-gradient(90deg, var(--glass-bg) 25%, rgba(255, 255, 255, 0.2) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
```

- [ ] **Step 2: 验证样式加载**

Run: `cd frontend && npm run dev`
Expected: 前端正常启动，无 CSS 错误

- [ ] **Step 3: 提交**

```bash
git add frontend/src/style.css
git commit -m "feat: 重构 CSS 变量系统，添加玻璃拟态效果和动画基础"
```

---

### Task 1.2: 主题切换功能

**Files:**
- Create: `frontend/src/stores/theme.ts`
- Create: `frontend/src/composables/useTheme.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/main.ts`

- [ ] **Step 1: 创建主题 store**

```typescript
// frontend/src/stores/theme.ts
import { defineStore } from 'pinia'

type Theme = 'light' | 'dark' | 'system'

type ThemeState = {
  theme: Theme
  resolved: 'light' | 'dark'
}

function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function resolveTheme(theme: Theme): 'light' | 'dark' {
  return theme === 'system' ? getSystemTheme() : theme
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => {
    const stored = localStorage.getItem('interviewpilot-theme') as Theme | null
    const theme = stored ?? 'system'
    return { theme, resolved: resolveTheme(theme) }
  },
  actions: {
    setTheme(theme: Theme) {
      this.theme = theme
      this.resolved = resolveTheme(theme)
      localStorage.setItem('interviewpilot-theme', theme)
      this.applyTheme()
    },
    toggleTheme() {
      const next = this.resolved === 'dark' ? 'light' : 'dark'
      this.setTheme(next)
    },
    applyTheme() {
      const html = document.documentElement
      if (this.resolved === 'dark') {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },
    initSystemListener() {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      media.addEventListener('change', () => {
        if (this.theme === 'system') {
          this.resolved = getSystemTheme()
          this.applyTheme()
        }
      })
      this.applyTheme()
    },
  },
})
```

- [ ] **Step 2: 更新 App.vue 绑定主题 class**

```vue
<!-- frontend/src/App.vue -->
<script setup lang="ts">
import { onMounted } from 'vue'

import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
onMounted(() => theme.initSystemListener())
</script>

<template>
  <RouterView />
</template>
```

- [ ] **Step 3: 验证主题切换**

Run: `cd frontend && npm run dev`
Expected: 打开浏览器控制台，执行 `document.documentElement.classList` 可看到 dark class

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/theme.ts frontend/src/App.vue
git commit -m "feat: 实现主题切换功能，支持 light/dark/system 三种模式"
```

---

## 阶段二：核心 UI 组件重构

### Task 2.1: 玻璃卡片组件 + Card 组件重构

**Files:**
- Create: `frontend/src/components/ui/glass-card/GlassCard.vue`
- Create: `frontend/src/components/ui/glass-card/index.ts`
- Modify: `frontend/src/components/ui/card/Card.vue`

- [ ] **Step 1: 创建 GlassCard 组件**

```vue
<!-- frontend/src/components/ui/glass-card/GlassCard.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

type GlassVariant = 'default' | 'elevated' | 'flat'

const props = withDefaults(
  defineProps<{
    variant?: GlassVariant
    hoverable?: boolean
    class?: string
  }>(),
  {
    variant: 'default',
    hoverable: false,
    class: '',
  },
)

const variantClasses: Record<GlassVariant, string> = {
  default: 'glass',
  elevated: 'glass-elevated',
  flat: 'glass-flat',
}
</script>

<template>
  <section
    :class="cn(
      'rounded-2xl p-0 transition-all duration-200',
      variantClasses[variant],
      hoverable && 'hover:-translate-y-0.5 hover:shadow-lg cursor-pointer',
      $props.class,
    )"
  >
    <slot />
  </section>
</template>
```

- [ ] **Step 2: 创建 index.ts 导出**

```typescript
// frontend/src/components/ui/glass-card/index.ts
export { default as GlassCard } from './GlassCard.vue'
```

- [ ] **Step 3: 重构 Card.vue 使用玻璃效果**

```vue
<!-- frontend/src/components/ui/card/Card.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

defineProps<{ class?: string }>()
</script>

<template>
  <section :class="cn('glass rounded-2xl text-sm', $props.class)">
    <slot />
  </section>
</template>
```

- [ ] **Step 4: 验证卡片显示**

Run: `cd frontend && npm run dev`
Expected: 所有卡片显示玻璃效果

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/ui/glass-card/ frontend/src/components/ui/card/Card.vue
git commit -m "feat: 创建 GlassCard 组件，重构 Card 使用玻璃效果"
```

---

### Task 2.2: Button 组件玻璃风格重构

**Files:**
- Modify: `frontend/src/components/ui/button/Button.vue`

- [ ] **Step 1: 重写 Button 组件**

```vue
<!-- frontend/src/components/ui/button/Button.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'focus-ring inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 active:scale-95',
  {
    variants: {
      variant: {
        default:
          'bg-gradient-to-r from-[var(--primary)] to-[var(--primary-dark)] text-white shadow-md hover:shadow-lg hover:-translate-y-0.5',
        secondary:
          'glass hover:bg-[var(--glass-bg-hover)] hover:-translate-y-0.5',
        outline:
          'border border-[var(--glass-border)] bg-transparent hover:bg-[var(--glass-bg)] hover:-translate-y-0.5',
        ghost:
          'hover:bg-[var(--glass-bg)] hover:-translate-y-0.5',
        destructive:
          'bg-[var(--error)] text-white hover:bg-[var(--error)]/90 hover:-translate-y-0.5',
      },
      size: {
        default: 'h-10 px-5 py-2',
        sm: 'h-9 rounded-lg px-3',
        lg: 'h-12 rounded-xl px-7',
        icon: 'size-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

type ButtonVariants = VariantProps<typeof buttonVariants>

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariants['variant']
    size?: ButtonVariants['size']
    class?: string
    type?: 'button' | 'submit' | 'reset'
  }>(),
  {
    variant: 'default',
    size: 'default',
    type: 'button',
    class: '',
  },
)

const classes = computed(() => cn(buttonVariants({ variant: props.variant, size: props.size }), props.class))
</script>

<template>
  <button :type="type" :class="classes">
    <slot />
  </button>
</template>
```

- [ ] **Step 2: 验证按钮样式**

Run: `cd frontend && npm run dev`
Expected: 所有按钮显示新样式，悬停有上浮效果

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/ui/button/Button.vue
git commit -m "feat: 重构 Button 组件，添加玻璃风格和悬停动画"
```

---

### Task 2.3: Input、Badge、Progress 组件重构

**Files:**
- Modify: `frontend/src/components/ui/input/Input.vue`
- Modify: `frontend/src/components/ui/badge/Badge.vue`
- Modify: `frontend/src/components/ui/progress/Progress.vue`

- [ ] **Step 1: 重构 Input 组件**

```vue
<!-- frontend/src/components/ui/input/Input.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    modelValue?: string | number
    class?: string
    type?: string
    placeholder?: string
    readonly?: boolean
    disabled?: boolean
    min?: number | string
    max?: number | string
    autocomplete?: string
  }>(),
  {
    type: 'text',
    class: '',
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string | number] }>()
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :readonly="readonly"
    :disabled="disabled"
    :min="min"
    :max="max"
    :autocomplete="autocomplete"
    :class="cn(
      'flex h-10 w-full rounded-xl border border-[var(--glass-border)] bg-[var(--bg-input)] px-4 py-2 text-sm',
      'backdrop-blur-sm transition-all duration-200',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:ring-4 focus:ring-[var(--primary)]/10 focus:bg-[var(--bg-elevated)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
```

- [ ] **Step 2: 重构 Badge 组件**

```vue
<!-- frontend/src/components/ui/badge/Badge.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[var(--primary)]/10 text-[var(--primary)]',
        secondary: 'bg-[var(--text-muted)]/10 text-[var(--text-secondary)]',
        outline: 'border border-[var(--glass-border)] text-[var(--text-secondary)]',
        accent: 'bg-[var(--accent)]/10 text-[var(--accent)]',
        success: 'bg-[var(--success)]/10 text-[var(--success)]',
        warning: 'bg-[var(--warning)]/10 text-[var(--warning)]',
        error: 'bg-[var(--error)]/10 text-[var(--error)]',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

type BadgeVariants = VariantProps<typeof badgeVariants>

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariants['variant']
    class?: string
  }>(),
  {
    variant: 'default',
    class: '',
  },
)

const classes = computed(() => cn(badgeVariants({ variant: props.variant }), props.class))
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
```

- [ ] **Step 3: 重构 Progress 组件**

```vue
<!-- frontend/src/components/ui/progress/Progress.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    value?: number
    class?: string
  }>(),
  {
    value: 0,
    class: '',
  },
)
</script>

<template>
  <div :class="cn('h-2 w-full overflow-hidden rounded-full bg-[var(--glass-bg)]', $props.class)">
    <div
      class="h-full rounded-full bg-gradient-to-r from-[var(--primary)] to-[var(--primary-dark)] transition-all duration-500 ease-out"
      :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"
    />
  </div>
</template>
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/ui/input/Input.vue frontend/src/components/ui/badge/Badge.vue frontend/src/components/ui/progress/Progress.vue
git commit -m "feat: 重构 Input、Badge、Progress 组件为玻璃风格"
```

---

### Task 2.4: Textarea 和 Separator 组件重构

**Files:**
- Modify: `frontend/src/components/ui/textarea/Textarea.vue`
- Modify: `frontend/src/components/ui/separator/Separator.vue`

- [ ] **Step 1: 重构 Textarea 组件**

```vue
<!-- frontend/src/components/ui/textarea/Textarea.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    class?: string
    placeholder?: string
    disabled?: boolean
  }>(),
  {
    class: '',
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <textarea
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="cn(
      'flex min-h-20 w-full rounded-xl border border-[var(--glass-border)] bg-[var(--bg-input)] px-4 py-3 text-sm',
      'backdrop-blur-sm transition-all duration-200',
      'placeholder:text-[var(--text-muted)]',
      'focus:border-[var(--primary)] focus:ring-4 focus:ring-[var(--primary)]/10 focus:bg-[var(--bg-elevated)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'resize-none',
      $props.class,
    )"
    @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
</template>
```

- [ ] **Step 2: 重构 Separator 组件**

```vue
<!-- frontend/src/components/ui/separator/Separator.vue -->
<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    orientation?: 'horizontal' | 'vertical'
    class?: string
  }>(),
  {
    orientation: 'horizontal',
    class: '',
  },
)
</script>

<template>
  <div
    :class="cn(
      'shrink-0 bg-[var(--border)]',
      orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px',
      $props.class,
    )"
  />
</template>
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/ui/textarea/Textarea.vue frontend/src/components/ui/separator/Separator.vue
git commit -m "feat: 重构 Textarea 和 Separator 组件为玻璃风格"
```

---

## 阶段三：布局组件重构

### Task 3.1: 主题切换按钮 + 侧边栏重构

**Files:**
- Create: `frontend/src/components/layout/ThemeToggle.vue`
- Modify: `frontend/src/components/layout/AppShell.vue`

- [ ] **Step 1: 创建 ThemeToggle 组件**

```vue
<!-- frontend/src/components/layout/ThemeToggle.vue -->
<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <Button variant="ghost" size="icon" @click="theme.toggleTheme()">
    <Sun v-if="theme.resolved === 'dark'" class="size-5" />
    <Moon v-else class="size-5" />
  </Button>
</template>
```

- [ ] **Step 2: 重写 AppShell.vue**

```vue
<!-- frontend/src/components/layout/AppShell.vue -->
<script setup lang="ts">
import {
  BarChart3,
  BookOpenCheck,
  Bot,
  FileText,
  Gauge,
  LogOut,
  Menu,
  MessageSquareText,
  Settings,
  UserCircle,
  X,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import GlobalAssistantWidget from '@/components/assistant/GlobalAssistantWidget.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)

const navItems = [
  { label: '仪表盘', path: '/dashboard', icon: Gauge },
  { label: '简历与 JD', path: '/documents', icon: FileText },
  { label: '题库', path: '/questions', icon: BookOpenCheck },
  { label: '模拟面试', path: '/interview', icon: MessageSquareText },
  { label: 'AI 助手', path: '/assistant', icon: Bot },
  { label: '报告', path: '/reports', icon: BarChart3 },
  { label: '设置', path: '/settings', icon: Settings },
]

const mobileNavItems = navItems.slice(0, 5)

const pageTitle = computed(() => navItems.find((item) => route.path.startsWith(item.path))?.label ?? '仪表盘')

function logout() {
  auth.logout()
  router.push('/login')
}

function closeSidebar() {
  sidebarOpen.value = false
}
</script>

<template>
  <div class="flex min-h-screen">
    <!-- 移动端遮罩 -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
        @click="closeSidebar"
      />
    </Transition>

    <!-- 侧边栏 -->
    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col glass-elevated transition-transform duration-300 lg:static lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="flex items-center justify-between gap-3 px-5 py-5">
        <div class="flex items-center gap-3">
          <div class="grid size-10 place-items-center rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-sm font-bold text-white shadow-md">
            IP
          </div>
          <div>
            <p class="text-base font-semibold">InterviewPilot</p>
            <p class="text-xs text-[var(--text-muted)]">AI 面试准备</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="lg:hidden" @click="closeSidebar">
          <X class="size-5" />
        </Button>
      </div>

      <!-- 导航 -->
      <nav class="mt-4 flex flex-1 flex-col gap-1 px-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="group relative flex h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-[var(--text-secondary)] transition-all duration-200 hover:bg-[var(--glass-bg-hover)] hover:text-[var(--text-primary)]"
          :class="{ 'bg-[var(--primary)]/10 text-[var(--primary)]': route.path.startsWith(item.path) }"
          @click="closeSidebar"
        >
          <div
            v-if="route.path.startsWith(item.path)"
            class="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-[var(--primary)]"
          />
          <component :is="item.icon" class="size-5" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- 用户信息 -->
      <div class="mx-3 mb-4 rounded-xl glass-flat p-3">
        <div class="flex items-center gap-3">
          <div class="grid size-9 place-items-center rounded-full bg-[var(--primary)]/10">
            <UserCircle class="size-5 text-[var(--primary)]" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium">{{ auth.user?.name }}</p>
            <p class="truncate text-xs text-[var(--text-muted)]">{{ auth.user?.username }}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" class="mt-2 w-full justify-start" @click="logout">
          <LogOut class="size-4" />
          退出登录
        </Button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="flex min-w-0 flex-1 flex-col">
      <!-- Header -->
      <header class="sticky top-0 z-30 glass border-b border-[var(--glass-border)]">
        <div class="mx-auto flex max-w-7xl items-center justify-between gap-3 px-5 py-3">
          <div class="flex items-center gap-3">
            <Button variant="ghost" size="icon" class="lg:hidden" @click="sidebarOpen = true">
              <Menu class="size-5" />
            </Button>
            <div>
              <p class="text-xs font-medium text-[var(--text-muted)]">InterviewPilot</p>
              <h1 class="text-lg font-semibold">{{ pageTitle }}</h1>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="secondary" size="sm" class="hidden sm:inline-flex" @click="router.push('/assistant')">
              <Bot class="size-4" />
              AI 助手
            </Button>
            <Button size="sm" @click="router.push('/interview')">
              <MessageSquareText class="size-4" />
              <span class="hidden sm:inline">开始练习</span>
            </Button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="mx-auto w-full max-w-7xl flex-1 px-4 py-5 sm:px-6 lg:px-8">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>

      <!-- 移动端底部导航 -->
      <nav class="fixed bottom-0 left-0 right-0 z-30 glass border-t border-[var(--glass-border)] pb-[env(safe-area-inset-bottom)] lg:hidden">
        <div class="flex items-center justify-around px-2 py-2">
          <RouterLink
            v-for="item in mobileNavItems"
            :key="item.path"
            :to="item.path"
            class="flex flex-col items-center gap-0.5 rounded-lg px-3 py-1.5 text-[10px] font-medium transition-colors"
            :class="route.path.startsWith(item.path) ? 'text-[var(--primary)]' : 'text-[var(--text-muted)]'"
          >
            <component :is="item.icon" class="size-5" />
            {{ item.label }}
          </RouterLink>
        </div>
      </nav>

      <!-- 移动端底部导航占位 -->
      <div class="h-16 lg:hidden" />
    </main>

    <GlobalAssistantWidget />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active {
  animation: fade-in-up 300ms ease-out;
}
.page-leave-active {
  animation: fade-out-up 200ms ease-in;
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-out-up {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-8px); }
}
</style>
```

- [ ] **Step 3: 验证布局**

Run: `cd frontend && npm run build`
Expected: 构建成功，无类型错误

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/layout/ThemeToggle.vue frontend/src/components/layout/AppShell.vue
git commit -m "feat: 重构侧边栏和 Header，添加玻璃效果、主题切换和移动端底部导航"
```

---

## 阶段四：页面重设计

### Task 4.1: 登录页面重设计

**Files:**
- Modify: `frontend/src/pages/LoginPage.vue`

- [ ] **Step 1: 重写 LoginPage.vue**

```vue
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
    <div class="glass-elevative w-full max-w-md rounded-2xl p-8 animate-fade-in-up">
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
```

- [ ] **Step 2: 验证登录页**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/LoginPage.vue
git commit -m "feat: 重设计登录页面，玻璃拟态风格 + 背景装饰"
```

---

### Task 4.2: 仪表盘页面重设计

**Files:**
- Modify: `frontend/src/pages/DashboardPage.vue`

- [ ] **Step 1: 重写 DashboardPage.vue**

```vue
<!-- frontend/src/pages/DashboardPage.vue -->
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowRight, BadgeCheck, BarChart3, BookOpenCheck, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

const router = useRouter()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const activePlan = computed(() => plansQuery.data.value?.[0])
const fitScore = computed(() => activePlan.value?.fit_score ?? 68)

const stats = computed(() => [
  { label: '准备计划', value: plansQuery.data.value?.length ?? 0, icon: FileText, color: 'var(--primary)' },
  { label: '资料', value: documentsQuery.data.value?.length ?? 0, icon: BookOpenCheck, color: 'var(--accent)' },
  { label: '题库', value: questionsQuery.data.value?.length ?? 0, icon: Target, color: 'var(--success)' },
  { label: '报告', value: reportsQuery.data.value?.length ?? 0, icon: BarChart3, color: 'var(--warning)' },
])
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 统计卡片 -->
    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="(stat, index) in stats"
        :key="stat.label"
        class="glass rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg animate-stagger"
        :style="{ '--stagger-index': index }"
      >
        <div class="mb-3 flex items-center justify-between">
          <component :is="stat.icon" class="size-5" :style="{ color: stat.color }" />
          <span class="text-3xl font-bold" :style="{ color: stat.color }">{{ stat.value }}</span>
        </div>
        <p class="text-sm text-[var(--text-secondary)]">{{ stat.label }}</p>
      </div>
    </section>

    <!-- 主要内容区 -->
    <section class="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
      <!-- 当前计划 -->
      <div class="glass-elevated rounded-2xl p-6">
        <div class="mb-5 flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold">当前准备计划</h2>
            <p class="text-sm text-[var(--text-secondary)]">{{ activePlan?.target_role ?? '上传简历与 JD 后生成专属路线' }}</p>
          </div>
          <Badge variant="accent" class="text-sm">Fit Score {{ fitScore }}</Badge>
        </div>

        <Progress :value="fitScore" class="mb-5" />

        <div class="mb-5 grid gap-3 sm:grid-cols-3">
          <div class="glass-flat rounded-xl p-4">
            <Target class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">岗位匹配</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">聚焦 JD 中最高频能力要求</p>
          </div>
          <div class="glass-flat rounded-xl p-4">
            <MessageSquareText class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">模拟追问</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">按回答动态生成追问题</p>
          </div>
          <div class="glass-flat rounded-xl p-4">
            <BadgeCheck class="mb-2 size-5 text-[var(--primary)]" />
            <p class="text-sm font-semibold">STAR Feedback</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">沉淀结构化复盘报告</p>
          </div>
        </div>

        <Button @click="router.push('/documents')">
          完善资料
          <ArrowRight class="size-4" />
        </Button>
      </div>

      <!-- 下一步行动 -->
      <div class="glass rounded-2xl p-6">
        <h2 class="mb-1 text-lg font-semibold">下一步行动</h2>
        <p class="mb-5 text-sm text-[var(--text-secondary)]">建议按顺序完成闭环</p>

        <div class="flex flex-col gap-3">
          <Button variant="secondary" class="justify-start" @click="router.push('/documents')">
            <FileText class="size-4" />
            上传简历与 JD
          </Button>
          <Button variant="secondary" class="justify-start" @click="router.push('/questions')">
            <Target class="size-4" />
            生成题库
          </Button>
          <Button class="justify-start" @click="router.push('/interview')">
            <MessageSquareText class="size-4" />
            开始模拟面试
          </Button>
        </div>
      </div>
    </section>
  </div>
</template>
```

- [ ] **Step 2: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/DashboardPage.vue
git commit -m "feat: 重设计仪表盘页面，玻璃卡片统计和渐入动画"
```

---

### Task 4.3: 文档页面重设计

**Files:**
- Modify: `frontend/src/pages/DocumentsPage.vue`

- [ ] **Step 1: 重写 DocumentsPage.vue**

```vue
<!-- frontend/src/pages/DocumentsPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { FileText, Upload } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api, type DocumentItem } from '@/lib/api'

const queryClient = useQueryClient()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const targetRole = ref('高级前端工程师')
const resumeFile = ref<File | null>(null)
const jdFile = ref<File | null>(null)
const message = ref('')

const resumes = computed(() => documentsQuery.data.value?.filter((item) => item.kind === 'resume') ?? [])
const jds = computed(() => documentsQuery.data.value?.filter((item) => item.kind === 'job_description') ?? [])

const uploadMutation = useMutation({
  mutationFn: ({ kind, file }: { kind: 'resume' | 'job-description'; file: File }) => api.uploadDocument(kind, file),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
})

const planMutation = useMutation({
  mutationFn: () =>
    api.createPlan({
      resume_id: resumes.value[0]?.id,
      job_description_id: jds.value[0]?.id,
      title: `${targetRole.value} 面试准备计划`,
      target_role: targetRole.value,
    }),
  onSuccess: () => {
    message.value = '准备计划已生成'
    queryClient.invalidateQueries({ queryKey: ['plans'] })
  },
})

async function upload(kind: 'resume' | 'job-description') {
  const file = kind === 'resume' ? resumeFile.value : jdFile.value
  if (!file) return
  await uploadMutation.mutateAsync({ kind, file })
  message.value = '上传并解析成功'
}

function preview(doc: DocumentItem) {
  return String(doc.summary.preview ?? '').slice(0, 120)
}
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
    <!-- 上传区域 -->
    <div class="glass rounded-2xl p-6">
      <h2 class="text-lg font-semibold">简历与 JD</h2>
      <p class="mb-5 text-sm text-[var(--text-secondary)]">上传材料后生成岗位匹配准备计划</p>

      <div class="flex flex-col gap-5">
        <label class="flex flex-col gap-2 text-sm font-medium">
          目标岗位
          <Input v-model="targetRole" />
        </label>

        <div class="glass-flat rounded-xl p-4">
          <p class="mb-3 text-sm font-semibold">简历</p>
          <input class="text-sm" type="file" accept=".pdf,.docx,.txt" @change="resumeFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!resumeFile || uploadMutation.isPending.value" @click="upload('resume')">
            <Upload class="size-4" />
            上传简历
          </Button>
        </div>

        <div class="glass-flat rounded-xl p-4">
          <p class="mb-3 text-sm font-semibold">职位 JD</p>
          <input class="text-sm" type="file" accept=".pdf,.docx,.txt" @change="jdFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!jdFile || uploadMutation.isPending.value" @click="upload('job-description')">
            <Upload class="size-4" />
            上传 JD
          </Button>
        </div>

        <Button :disabled="planMutation.isPending.value" @click="planMutation.mutate()">
          生成准备计划
        </Button>
        <p v-if="message" class="text-sm text-[var(--primary)]">{{ message }}</p>
      </div>
    </div>

    <!-- 资料库 -->
    <div class="glass rounded-2xl p-6">
      <h2 class="text-lg font-semibold">资料库</h2>
      <p class="mb-5 text-sm text-[var(--text-secondary)]">最新计划数：{{ plansQuery.data.value?.length ?? 0 }}</p>

      <div class="flex flex-col gap-3">
        <div
          v-for="(doc, index) in documentsQuery.data.value"
          :key="doc.id"
          class="glass-flat rounded-xl p-4 animate-stagger"
          :style="{ '--stagger-index': index }"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <FileText class="size-4 text-[var(--primary)]" />
              <p class="font-medium">{{ doc.filename }}</p>
            </div>
            <Badge :variant="doc.kind === 'resume' ? 'default' : 'accent'">
              {{ doc.kind === 'resume' ? '简历' : 'JD' }}
            </Badge>
          </div>
          <p class="mt-2 text-sm text-[var(--text-muted)]">{{ preview(doc) }}</p>
        </div>
        <p v-if="!documentsQuery.data.value?.length" class="text-sm text-[var(--text-muted)]">还没有上传资料。</p>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/DocumentsPage.vue
git commit -m "feat: 重设计文档页面，玻璃卡片布局和渐入动画"
```

---

### Task 4.4: 题库页面重设计

**Files:**
- Modify: `frontend/src/pages/QuestionsPage.vue`

- [ ] **Step 1: 重写 QuestionsPage.vue**

```vue
<!-- frontend/src/pages/QuestionsPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { RefreshCw } from 'lucide-vue-next'
import { ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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
        <Button class="self-end" :disabled="generateMutation.isPending.value" @click="generateMutation.mutate()">
          <RefreshCw class="size-4" :class="{ 'animate-spin': generateMutation.isPending.value }" />
          生成题目
        </Button>
      </div>
    </div>

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
```

- [ ] **Step 2: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/QuestionsPage.vue
git commit -m "feat: 重设计题库页面，玻璃卡片和渐入动画"
```

---

### Task 4.5: 模拟面试页面重设计

**Files:**
- Modify: `frontend/src/pages/InterviewPage.vue`

- [ ] **Step 1: 重写 InterviewPage.vue**

```vue
<!-- frontend/src/pages/InterviewPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { Bot, Send, Sparkles } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { api, streamApi, type Interview } from '@/lib/api'

const queryClient = useQueryClient()
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const questionsQuery = useQuery({ queryKey: ['questions'], queryFn: api.questions })
const interview = ref<Interview | null>(null)
const selectedQuestion = ref('请介绍一个最能体现你岗位匹配度的项目。')
const answer = ref('')
const followUp = ref('')
const streaming = ref(false)

const latestTurn = computed(() => interview.value?.turns.at(-1))
const score = computed(() => interview.value?.current_score ?? 0)

const createMutation = useMutation({
  mutationFn: () => api.createInterview({ prep_plan_id: plansQuery.data.value?.[0]?.id, title: '文字模拟面试' }),
  onSuccess: (data) => { interview.value = data },
})

const answerMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    return api.answer(interview.value.id, { question: selectedQuestion.value, answer: answer.value })
  },
  onSuccess: async (data) => {
    interview.value = data
    answer.value = ''
    await streamFollowUp()
  },
})

const reportMutation = useMutation({
  mutationFn: () => {
    if (!interview.value) throw new Error('请先开始面试')
    return api.createReport(interview.value.id)
  },
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reports'] }),
})

async function startInterview() {
  await createMutation.mutateAsync()
  selectedQuestion.value = questionsQuery.data.value?.[0]?.prompt ?? selectedQuestion.value
}

async function streamFollowUp() {
  if (!interview.value) return
  followUp.value = ''
  streaming.value = true
  try {
    await streamApi(`/stream/interviews/${interview.value.id}/follow-up`, (chunk) => {
      followUp.value += chunk
    })
    if (followUp.value) selectedQuestion.value = followUp.value
  } finally {
    streaming.value = false
  }
}
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[1fr_360px]">
    <!-- 主面试区 -->
    <div class="glass rounded-2xl p-6">
      <div class="mb-5 flex items-start justify-between">
        <div>
          <h2 class="text-lg font-semibold">模拟面试</h2>
          <p class="text-sm text-[var(--text-secondary)]">文字问答优先，AI 会根据回答生成追问</p>
        </div>
        <Badge variant="accent" class="text-sm">当前得分 {{ score || '--' }}</Badge>
      </div>

      <div class="flex flex-col gap-5">
        <!-- 面试官问题 -->
        <div class="glass-elevated rounded-xl p-5">
          <div class="mb-2 flex items-center gap-2 text-sm font-semibold">
            <Bot class="size-4 text-[var(--primary)]" />
            面试官问题
          </div>
          <p class="text-base leading-7">{{ selectedQuestion }}</p>
        </div>

        <!-- 回答输入 -->
        <Textarea v-model="answer" class="min-h-44" placeholder="输入你的回答，尽量使用 STAR 结构并补充量化结果。" />

        <!-- 操作按钮 -->
        <div class="flex flex-wrap gap-3">
          <Button :disabled="createMutation.isPending.value" @click="startInterview">
            <Sparkles class="size-4" />
            {{ interview ? '重新开始' : '开始面试' }}
          </Button>
          <Button :disabled="!interview || !answer || answerMutation.isPending.value" @click="answerMutation.mutate()">
            <Send class="size-4" />
            提交回答
          </Button>
          <Button variant="secondary" :disabled="!interview || reportMutation.isPending.value" @click="reportMutation.mutate()">
            生成报告
          </Button>
        </div>
      </div>
    </div>

    <!-- 侧边栏 -->
    <aside class="flex flex-col gap-5">
      <!-- 评分摘要 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">评分摘要</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">即时反馈会沉淀到报告</p>
        <Progress :value="score" class="mb-3" />
        <p class="text-sm text-[var(--text-secondary)]">
          {{ latestTurn?.feedback?.summary ?? '提交第一段回答后查看 STAR Feedback。' }}
        </p>
      </div>

      <!-- 追问 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-1 text-base font-semibold">追问</h3>
        <p class="mb-3 text-xs text-[var(--text-muted)]">{{ streaming ? 'AI 正在生成...' : '根据上一轮回答动态生成' }}</p>
        <p class="text-sm leading-6 text-[var(--text-secondary)]">{{ followUp || '暂无追问。' }}</p>
      </div>

      <!-- 最近问答 -->
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-3 text-base font-semibold">最近问答</h3>
        <div class="flex flex-col gap-3">
          <div v-for="turn in interview?.turns" :key="turn.id" class="glass-flat rounded-lg p-3">
            <p class="text-sm font-medium">{{ turn.question }}</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">得分 {{ turn.score }}</p>
          </div>
          <p v-if="!interview?.turns.length" class="text-sm text-[var(--text-muted)]">还没有提交回答。</p>
        </div>
      </div>
    </aside>
  </div>
</template>
```

- [ ] **Step 2: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/InterviewPage.vue
git commit -m "feat: 重设计模拟面试页面，玻璃卡片布局"
```

---

### Task 4.6: 报告页面重设计

**Files:**
- Modify: `frontend/src/pages/ReportsPage.vue`

- [ ] **Step 1: 重写 ReportsPage.vue**

```vue
<!-- frontend/src/pages/ReportsPage.vue -->
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { FileBarChart } from 'lucide-vue-next'
import { ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import RadarChart from '@/components/charts/RadarChart.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import { api } from '@/lib/api'

const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })

const averageScores = ref({
  clarity: 75,
  structure: 70,
  evidence: 72,
  reflection: 68,
})

const scoreTrend = ref([
  { date: '第1次', score: 65 },
  { date: '第2次', score: 72 },
  { date: '第3次', score: 78 },
  { date: '第4次', score: 82 },
])
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 图表区域 -->
    <div class="grid gap-4 md:grid-cols-2">
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">能力维度分析</h3>
        <RadarChart :data="averageScores" />
      </div>
      <div class="glass rounded-2xl p-5">
        <h3 class="mb-4 text-base font-semibold">分数趋势</h3>
        <TrendChart :data="scoreTrend" />
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="grid gap-4 lg:grid-cols-2">
      <div
        v-for="(report, index) in reportsQuery.data.value"
        :key="report.id"
        class="glass rounded-2xl p-5 animate-stagger"
        :style="{ '--stagger-index': index }"
      >
        <div class="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3 class="font-semibold">{{ report.title }}</h3>
            <p class="text-xs text-[var(--text-muted)]">STAR Feedback 复盘</p>
          </div>
          <Badge variant="accent" class="text-sm">{{ report.overall_score }} 分</Badge>
        </div>
        <Progress :value="report.overall_score" class="mb-3" />
        <p class="whitespace-pre-line text-sm leading-6 text-[var(--text-secondary)]">{{ report.content }}</p>
      </div>

      <div v-if="!reportsQuery.data.value?.length" class="glass rounded-2xl p-6 text-center lg:col-span-2">
        <FileBarChart class="mx-auto mb-3 size-8 text-[var(--primary)]" />
        <h3 class="font-semibold">还没有报告</h3>
        <p class="mt-1 text-sm text-[var(--text-muted)]">完成至少一轮模拟面试后生成复盘报告</p>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/ReportsPage.vue
git commit -m "feat: 重设计报告页面，玻璃卡片图表和列表"
```

---

### Task 4.7: 设置页面和 AI 助手页面重设计

**Files:**
- Modify: `frontend/src/pages/SettingsPage.vue`
- Modify: `frontend/src/pages/AssistantPage.vue`
- Modify: `frontend/src/components/assistant/GlobalAssistantWidget.vue`
- Modify: `frontend/src/components/assistant/AssistantChatPanel.vue`

- [ ] **Step 1: 重写 SettingsPage.vue**

```vue
<!-- frontend/src/pages/SettingsPage.vue -->
<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="glass rounded-2xl p-6">
    <h2 class="text-lg font-semibold">设置</h2>
    <p class="mb-5 text-sm text-[var(--text-secondary)]">模型配置通过后端环境变量管理，前端只展示当前说明。</p>

    <div class="grid gap-4 md:grid-cols-2">
      <label class="flex flex-col gap-2 text-sm font-medium">
        API 地址
        <Input model-value="VITE_API_BASE_URL=http://localhost:8000/api" readonly />
      </label>
      <label class="flex flex-col gap-2 text-sm font-medium">
        模型配置
        <Input model-value="AI_BASE_URL / AI_API_KEY / AI_MODEL" readonly />
      </label>
    </div>

    <div class="mt-6 flex items-center gap-3">
      <span class="text-sm font-medium">主题</span>
      <ThemeToggle />
      <span class="text-sm text-[var(--text-muted)]">{{ theme.theme === 'system' ? '跟随系统' : theme.resolved === 'dark' ? '深色' : '浅色' }}</span>
    </div>
  </div>
</template>
```

- [ ] **Step 2: 重写 AssistantPage.vue**

```vue
<!-- frontend/src/pages/AssistantPage.vue -->
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Bot, FileText, MessageSquareText, Target } from 'lucide-vue-next'
import { computed } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'

const contextQuery = useQuery({ queryKey: ['assistant-context'], queryFn: api.assistantContext })

const documents = computed(() => contextQuery.data.value?.documents ?? [])
const activePlan = computed(() => contextQuery.data.value?.activePlan)
const recentInterview = computed(() => contextQuery.data.value?.recentInterview)
const latestReport = computed(() => contextQuery.data.value?.latestReport)
</script>

<template>
  <div class="grid min-h-[calc(100vh-12rem)] gap-5 xl:grid-cols-[1fr_360px]">
    <div class="glass rounded-2xl p-5">
      <AssistantChatPanel />
    </div>

    <aside class="flex flex-col gap-4">
      <div class="glass rounded-2xl p-5">
        <div class="mb-4 flex items-center gap-2">
          <Bot class="size-5 text-[var(--primary)]" />
          <h3 class="font-semibold">引用上下文</h3>
        </div>
        <p class="mb-4 text-xs text-[var(--text-muted)]">助手会优先参考这些本地资料</p>

        <div class="flex flex-col gap-3">
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-medium">准备计划</span>
              <Badge variant="accent">{{ activePlan ? '已生成' : '未生成' }}</Badge>
            </div>
            <p class="mt-2 text-xs text-[var(--text-muted)]">{{ activePlan?.title ?? '上传简历与 JD 后生成计划' }}</p>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <FileText class="size-4 text-[var(--primary)]" />
              资料 {{ documents.length }}
            </div>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <Target class="size-4 text-[var(--primary)]" />
              题库 {{ contextQuery.data.value?.questionCount ?? 0 }}
            </div>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <div class="flex items-center gap-2 text-sm font-medium">
              <MessageSquareText class="size-4 text-[var(--primary)]" />
              最近面试
            </div>
            <p class="mt-1 text-xs text-[var(--text-muted)]">
              {{ recentInterview ? `最近得分 ${recentInterview.currentScore ?? 0}` : '还没有模拟面试记录' }}
            </p>
          </div>
          <div class="glass-flat rounded-xl p-3">
            <p class="text-sm font-medium">最新报告</p>
            <p class="mt-1 text-xs text-[var(--text-muted)]">{{ latestReport ? latestReport.title : '生成报告后，助手会引用复盘结论' }}</p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>
```

- [ ] **Step 3: 重写 GlobalAssistantWidget.vue**

```vue
<!-- frontend/src/components/assistant/GlobalAssistantWidget.vue -->
<script setup lang="ts">
import { Bot, X } from 'lucide-vue-next'
import { ref } from 'vue'

import AssistantChatPanel from '@/components/assistant/AssistantChatPanel.vue'
import { Button } from '@/components/ui/button'

const open = ref(false)
</script>

<template>
  <div class="fixed bottom-20 right-4 z-40 flex flex-col items-end gap-3 lg:bottom-5">
    <Transition name="scale">
      <div v-if="open" class="glass-elevated h-[min(620px,calc(100vh-7rem))] w-[min(420px,calc(100vw-2rem))] rounded-2xl p-4">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <div class="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-white">
              <Bot class="size-4" />
            </div>
            <div>
              <p class="text-sm font-semibold">InterviewPilot AI 助手</p>
              <p class="text-xs text-[var(--text-muted)]">全局流式问答</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" @click="open = false">
            <X class="size-4" />
          </Button>
        </div>
        <AssistantChatPanel compact />
      </div>
    </Transition>

    <Button size="lg" class="h-12 rounded-full px-5 shadow-lg" @click="open = !open">
      <Bot class="size-5" />
      AI 助手
    </Button>
  </div>
</template>

<style scoped>
.scale-enter-active {
  animation: scale-in 200ms ease-out;
}
.scale-leave-active {
  animation: scale-out 150ms ease-in;
}
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.9) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes scale-out {
  from { opacity: 1; transform: scale(1) translateY(0); }
  to { opacity: 0; transform: scale(0.9) translateY(10px); }
}
</style>
```

- [ ] **Step 4: 重写 AssistantChatPanel.vue**

```vue
<!-- frontend/src/components/assistant/AssistantChatPanel.vue -->
<script setup lang="ts">
import { Send, Trash2 } from 'lucide-vue-next'
import { nextTick, onMounted, ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useAssistantStore } from '@/stores/assistant'

const props = withDefaults(defineProps<{ compact?: boolean }>(), {
  compact: false,
})

const assistant = useAssistantStore()
const input = ref('')
const scrollRef = ref<HTMLElement | null>(null)

onMounted(() => {
  assistant.loadConversation().catch(() => undefined)
})

async function send() {
  const message = input.value
  input.value = ''
  await assistant.send(message)
}

watch(
  () => assistant.messages.map((item) => item.content).join(''),
  async () => {
    await nextTick()
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  },
)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col gap-3">
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="text-sm font-semibold">AI 助手</p>
        <p class="text-xs text-[var(--text-muted)]">基于简历、JD、面试记录和报告回答</p>
      </div>
      <Button variant="ghost" size="icon" title="清空聊天" @click="assistant.clear">
        <Trash2 class="size-4" />
      </Button>
    </div>

    <div ref="scrollRef" class="min-h-0 flex-1 overflow-y-auto rounded-xl glass-flat p-3">
      <div v-if="!assistant.messages.length" class="flex h-full min-h-44 flex-col justify-center gap-2 text-sm text-[var(--text-muted)]">
        <p class="font-medium text-[var(--text-primary)]">可以这样问我：</p>
        <p>我下一步该怎么准备？</p>
        <p>帮我根据 JD 梳理 5 个高频追问。</p>
        <p>我的 STAR 回答哪里最需要加强？</p>
      </div>
      <div v-else class="flex flex-col gap-3">
        <div
          v-for="message in assistant.messages"
          :key="message.id"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[88%] whitespace-pre-wrap rounded-xl px-4 py-2.5 text-sm leading-6"
            :class="message.role === 'user'
              ? 'bg-gradient-to-r from-[var(--primary)] to-[var(--primary-dark)] text-white'
              : 'glass-flat'"
          >
            {{ message.content || (message.status === 'streaming' ? '正在生成...' : '') }}
          </div>
        </div>
      </div>
    </div>

    <p v-if="assistant.error" class="text-xs text-[var(--error)]">{{ assistant.error }}</p>
    <form class="flex gap-2" @submit.prevent="send">
      <Textarea
        v-model="input"
        :class="compact ? 'min-h-16' : 'min-h-20'"
        placeholder="问问 AI 助手，比如：我下一步该怎么准备？"
        @keydown.ctrl.enter.prevent="send"
      />
      <Button type="submit" size="icon" :disabled="assistant.isStreaming || !input.trim()">
        <Send class="size-4" />
      </Button>
    </form>
  </div>
</template>
```

- [ ] **Step 5: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 6: 提交**

```bash
git add frontend/src/pages/SettingsPage.vue frontend/src/pages/AssistantPage.vue frontend/src/components/assistant/GlobalAssistantWidget.vue frontend/src/components/assistant/AssistantChatPanel.vue
git commit -m "feat: 重设计设置页、AI 助手页和聊天组件为玻璃风格"
```

---

## 阶段五：验证与优化

### Task 5.1: 构建验证与测试修复

**Files:**
- Modify: `frontend/src/components/layout/AppShell.test.ts` (if exists)
- Modify: `frontend/src/pages/LoginPage.test.ts` (if exists)

- [ ] **Step 1: 运行构建**

Run: `cd frontend && npm run build`
Expected: 构建成功，无类型错误

- [ ] **Step 2: 运行测试**

Run: `cd frontend && npm test`
Expected: 所有测试通过（或修复因 UI 重构导致的测试失败）

- [ ] **Step 3: 提交**

```bash
git add -A frontend/
git commit -m "fix: 修复 UI 重构后的测试和构建问题"
```

---

## 自检清单

完成所有任务后，执行以下验证：

- [ ] `cd frontend && npm run build` 构建成功
- [ ] `cd frontend && npm test` 测试通过
- [ ] 浅色主题显示正常（玻璃效果、渐变背景、卡片阴影）
- [ ] 深色主题显示正常
- [ ] 主题切换按钮工作正常
- [ ] 所有页面路由切换有过渡动画
- [ ] 按钮悬停有上浮效果，点击有缩放效果
- [ ] 卡片悬停有上浮效果
- [ ] 移动端底部导航栏显示正常（<1024px）
- [ ] 移动端侧边栏抽屉式滑出正常
- [ ] 所有 8 个页面布局正确
- [ ] 表单交互正常（登录、上传、输入）
- [ ] ECharts 图表显示正常
- [ ] AI 助手悬浮窗动画正常
- [ ] 无控制台错误
