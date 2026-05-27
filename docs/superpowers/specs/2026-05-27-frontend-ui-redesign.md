# InterviewPilot 前端 UI 全面重设计规范

## 概述

本文档定义了 InterviewPilot 前端 UI 的全面重设计方案，采用玻璃拟态 (Glassmorphism) 设计风格，支持深色/浅色主题切换，包含丰富的动画效果和完整的移动端适配。

**设计目标**：
- 提升用户体验和视觉效果
- 统一设计语言和风格
- 优化移动端适配
- 增强交互设计和动画效果

**技术栈**：
- Vue 3 + TypeScript + Vite
- Tailwind CSS 4
- shadcn-vue 风格组件（保留并增强）
- ECharts（数据可视化）

---

## 1. 设计原则

| 原则 | 描述 |
|------|------|
| **玻璃质感** | 毛玻璃背景、半透明卡片、柔和阴影，创造层次感和深度感 |
| **层次分明** | 通过透明度和模糊度创造视觉层次，引导用户注意力 |
| **呼吸感** | 大量留白，元素间距宽松，避免信息过载 |
| **微交互** | 丰富的悬停、点击、过渡动画，提升操作反馈 |
| **一致性** | 统一的设计语言，所有组件遵循相同的视觉规范 |

---

## 2. 配色方案

### 2.1 浅色主题 (Light)

```css
:root {
  /* 背景 */
  --background-gradient-start: #f0f4f8;
  --background-gradient-end: #e2e8f0;

  /* 玻璃效果 */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
  --glass-blur: blur(16px) saturate(180%);
  --glass-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -2px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);

  /* 主色调 */
  --primary: #3b82f6;
  --primary-light: #60a5fa;
  --primary-dark: #2563eb;
  --primary-gradient: linear-gradient(135deg, #3b82f6, #2563eb);

  /* 强调色 */
  --accent: #8b5cf6;
  --accent-light: #a78bfa;

  /* 文字 */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;

  /* 边框 */
  --border-default: rgba(0, 0, 0, 0.1);
  --border-hover: rgba(59, 130, 246, 0.3);

  /* 状态颜色 */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
}
```

### 2.2 深色主题 (Dark)

```css
.dark {
  /* 背景 */
  --background-gradient-start: #0f172a;
  --background-gradient-end: #1e293b;

  /* 玻璃效果 */
  --glass-bg: rgba(30, 41, 59, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);

  /* 主色调 */
  --primary: #60a5fa;
  --primary-light: #93c5fd;
  --primary-dark: #3b82f6;

  /* 强调色 */
  --accent: #a78bfa;
  --accent-light: #c4b5fd;

  /* 文字 */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  /* 边框 */
  --border-default: rgba(255, 255, 255, 0.1);
  --border-hover: rgba(96, 165, 250, 0.3);

  /* 状态颜色 */
  --success: #34d399;
  --warning: #fbbf24;
  --error: #f87171;
  --info: #60a5fa;
}
```

---

## 3. 玻璃拟态效果规范

### 3.1 标准玻璃卡片

```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow);
  transition: all 200ms ease;
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 12px -2px rgba(0, 0, 0, 0.15),
    0 4px 6px -2px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}
```

### 3.2 强调玻璃卡片

```css
.glass-card-elevated {
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(200%);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: 
    0 10px 15px -3px rgba(0, 0, 0, 0.2),
    0 4px 6px -4px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}
```

### 3.3 扁平玻璃卡片

```css
.glass-card-flat {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  box-shadow: none;
}
```

---

## 4. 动画规范

### 4.1 页面切换动画

```css
/* 路由过渡 */
.page-enter-active {
  animation: page-in 300ms ease-out;
}

.page-leave-active {
  animation: page-out 200ms ease-in;
}

@keyframes page-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes page-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}
```

### 4.2 卡片动画

```css
/* 悬停效果 */
.card-hover {
  transition: all 200ms ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.15);
}

/* 点击效果 */
.card-click {
  transition: transform 100ms ease-in;
}

.card-click:active {
  transform: scale(0.98);
}
```

### 4.3 按钮动画

```css
/* 主按钮 */
.btn-primary {
  background: var(--primary-gradient);
  color: white;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 200ms ease;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.btn-primary:active {
  transform: scale(0.95);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* 次要按钮 */
.btn-secondary {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 200ms ease;
}

.btn-secondary:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-2px);
}
```

### 4.4 列表动画

```css
/* 列表项进入动画 */
.list-enter-active {
  animation: list-in 300ms ease-out;
}

@keyframes list-in {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 交错动画 */
.stagger-enter-active {
  animation: list-in 300ms ease-out;
  animation-delay: calc(var(--index) * 50ms);
}
```

### 4.5 加载动画

```css
/* 骨架屏 */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--glass-bg) 25%,
    rgba(255, 255, 255, 0.3) 50%,
    var(--glass-bg) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: 8px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

---

## 5. 布局设计

### 5.1 整体布局结构

```
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌────────────────────────────────────────┐  │
│  │          │  │  Header (玻璃效果)                      │  │
│  │  侧边栏   │  │  - 页面标题                            │  │
│  │  (玻璃)   │  │  - 主题切换 + 用户头像                  │  │
│  │          │  ├────────────────────────────────────────┤  │
│  │  - Logo  │  │                                        │  │
│  │  - 导航   │  │  Main Content                          │  │
│  │  - 用户   │  │  - 玻璃卡片容器                         │  │
│  │          │  │  - 响应式网格布局                        │  │
│  │          │  │                                        │  │
│  └──────────┘  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 侧边栏设计

**桌面端（≥1024px）**：
- 固定宽度：280px
- 玻璃背景 + 右侧边框
- Logo 区域 + 导航菜单 + 用户信息
- 当前选中项：高亮背景 + 左侧指示条

**移动端（<1024px）**：
- 默认隐藏
- 点击汉堡菜单滑出
- 覆盖层 + 玻璃遮罩
- 点击外部区域关闭

### 5.3 响应式断点

```css
/* 移动端 */
@media (max-width: 639px) {
  /* 单列布局 */
  .grid-responsive {
    grid-template-columns: 1fr;
  }
}

/* 平板端 */
@media (min-width: 640px) and (max-width: 1023px) {
  /* 两列布局 */
  .grid-responsive {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  /* 侧边栏 + 主内容 */
  .layout {
    display: flex;
  }

  .sidebar {
    width: 280px;
    position: fixed;
    height: 100vh;
  }

  .main {
    margin-left: 280px;
    flex: 1;
  }
}
```

---

## 6. 组件设计

### 6.1 按钮组件

**类型**：
- `btn-primary` - 主按钮（渐变蓝）
- `btn-secondary` - 次要按钮（玻璃背景）
- `btn-ghost` - 幽灵按钮（透明）
- `btn-danger` - 危险按钮（红色）
- `btn-icon` - 图标按钮

**尺寸**：
- `sm` - 小按钮（32px 高度）
- `md` - 中按钮（40px 高度，默认）
- `lg` - 大按钮（48px 高度）

### 6.2 卡片组件

**变体**：
- `glass-card` - 标准玻璃卡片
- `glass-card-elevated` - 强调卡片
- `glass-card-flat` - 扁平卡片

**状态**：
- 默认状态
- 悬停状态（轻微上浮）
- 点击状态（缩放）
- 禁用状态（降低透明度）

### 6.3 输入框组件

```css
.input-glass {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 200ms ease;
}

.input-glass:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: rgba(255, 255, 255, 0.7);
}

.dark .input-glass {
  background: rgba(30, 41, 59, 0.5);
}

.dark .input-glass:focus {
  background: rgba(30, 41, 59, 0.7);
}
```

### 6.4 徽章组件

**类型**：
- `badge-primary` - 主要徽章（蓝色）
- `badge-success` - 成功徽章（绿色）
- `badge-warning` - 警告徽章（黄色）
- `badge-error` - 错误徽章（红色）
- `badge-accent` - 强调徽章（紫色）

### 6.5 进度条组件

```css
.progress-bar {
  height: 8px;
  background: var(--glass-bg);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-gradient);
  border-radius: 4px;
  transition: width 500ms ease-out;
}
```

---

## 7. 页面设计

### 7.1 登录页面

**设计要点**：
- 全屏居中布局
- 大尺寸玻璃卡片
- 背景渐变 + 装饰性几何图形
- 表单元素垂直排列
- 登录/注册切换动画

**布局**：
```
┌────────────────────────────────────────────────────┐
│                                                    │
│    ┌────────────────────────────────────────┐      │
│    │                                        │      │
│    │   🎯 InterviewPilot                   │      │
│    │   AI 面试准备平台                       │      │
│    │                                        │      │
│    │   ┌──────────────────────────────┐    │      │
│    │   │ 用户名                       │    │      │
│    │   └──────────────────────────────┘    │      │
│    │   ┌──────────────────────────────┐    │      │
│    │   │ 密码                         │    │      │
│    │   └──────────────────────────────┘    │      │
│    │                                        │      │
│    │   [         登录          ]           │      │
│    │                                        │      │
│    │   没有账号？注册                       │      │
│    │                                        │      │
│    └────────────────────────────────────────┘      │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 7.2 仪表盘页面

**设计要点**：
- 顶部统计卡片（玻璃效果）
- 当前计划卡片（突出显示）
- 下一步行动区域
- 最近活动时间线

**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│ Header: 仪表盘                                              │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│ │ 准备计划 │ │  资料   │ │  题库   │ │  报告   │           │
│ │   12    │ │    5    │ │   24    │ │    3    │           │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                             │
│ ┌─────────────────────────────────┐ ┌─────────────────────┐ │
│ │ 当前准备计划                     │ │ 下一步行动           │ │
│ │                                 │ │                     │ │
│ │ 目标岗位：前端工程师              │ │ [上传简历与 JD]      │ │
│ │ Fit Score: ████████░░ 78        │ │ [生成题库]           │ │
│ │                                 │ │ [开始模拟面试]       │ │
│ │ • 岗位匹配                       │ │                     │ │
│ │ • 模拟追问                       │ │                     │ │
│ │ • STAR Feedback                  │ │                     │ │
│ │                                 │ │                     │ │
│ │ [完善资料 →]                     │ │                     │ │
│ └─────────────────────────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 模拟面试页面

**设计要点**：
- 左右分栏布局（桌面端）
- 面试官问题区域（玻璃卡片，突出显示）
- 回答输入区域
- 右侧评分和追问面板
- 消息气泡式对话历史

### 7.4 报告页面

**设计要点**：
- 顶部图表区域（雷达图 + 趋势图）
- 报告列表（玻璃卡片）
- 报告详情展开

### 7.5 移动端适配

**底部导航栏（移动端）**：
```
┌─────────────────────┐
│                     │
│    页面内容          │
│                     │
├─────────────────────┤
│ 🏠  📄  💬  📊  ⚙️  │
│ 仪表盘 简历 面试 报告 设置 │
└─────────────────────┘
```

**移动端特殊处理**：
- 侧边栏变为抽屉式滑出
- 卡片改为单列布局
- 表单元素全宽显示
- 图表自适应宽度

---

## 8. 图标规范

使用 `lucide-vue-next` 图标库，保持一致性。

**图标尺寸**：
- `sm` - 16px（用于按钮内图标）
- `md` - 20px（用于导航图标）
- `lg` - 24px（用于卡片标题图标）

**图标颜色**：
- 默认：`currentColor`
- 强调：`var(--primary)`
- 禁用：`var(--text-muted)`

---

## 9. 字体规范

```css
:root {
  --font-sans: Inter, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "Fira Code", "JetBrains Mono", monospace;
}

/* 字体大小 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* 字体粗细 */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

---

## 10. 间距规范

使用 Tailwind CSS 的默认间距系统：

```css
/* 间距 */
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-10: 2.5rem;  /* 40px */
--spacing-12: 3rem;    /* 48px */
```

---

## 11. 圆角规范

```css
--radius-sm: 8px;    /* 按钮、输入框 */
--radius-md: 12px;   /* 卡片、下拉菜单 */
--radius-lg: 16px;   /* 大卡片、模态框 */
--radius-xl: 24px;   /* 特殊元素 */
--radius-full: 9999px; /* 胶囊按钮、头像 */
```

---

## 12. 阴影规范

```css
/* 浅色主题阴影 */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);

/* 深色主题阴影 */
.dark --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
.dark --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
.dark --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
```

---

## 13. 实施阶段

### 阶段一：基础设施（1-2 天）
1. 更新 Tailwind CSS 配置
2. 创建 CSS 变量系统
3. 实现主题切换功能
4. 创建基础玻璃组件

### 阶段二：核心组件（2-3 天）
1. 重构侧边栏组件
2. 重构 Header 组件
3. 创建玻璃卡片组件
4. 创建按钮组件
5. 创建表单组件

### 阶段三：页面重设计（3-4 天）
1. 登录页面
2. 仪表盘页面
3. 文档页面
4. 题库页面
5. 模拟面试页面
6. 报告页面
7. 设置页面
8. AI 助手页面

### 阶段四：动画与交互（1-2 天）
1. 页面过渡动画
2. 卡片悬停动画
3. 按钮点击动画
4. 列表进入动画
5. 加载动画

### 阶段五：移动端适配（1-2 天）
1. 底部导航栏
2. 响应式布局
3. 触摸优化
4. 移动端侧边栏

### 阶段六：测试与优化（1 天）
1. 跨浏览器测试
2. 性能优化
3. 无障碍优化
4. 最终调整

**总预计时间：9-14 天**

---

## 14. 验证清单

完成所有任务后，执行以下验证：

- [ ] 浅色主题显示正常
- [ ] 深色主题显示正常
- [ ] 主题切换功能正常
- [ ] 玻璃效果在两种主题下都正常
- [ ] 所有动画流畅
- [ ] 移动端适配正常
- [ ] 所有页面布局正确
- [ ] 表单交互正常
- [ ] 图表显示正常
- [ ] 无控制台错误
- [ ] 构建成功
- [ ] 所有测试通过

---

## 15. 参考资源

- [Glassmorphism CSS Generator](https://hype4.academy/tools/glassmorphism-generator)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/icons)
- [Vue 3 Transition](https://vuejs.org/guide/built-ins/transition.html)

---

**文档版本**：1.0
**创建日期**：2026-05-27
**作者**：AI Assistant
