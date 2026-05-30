<p align="center">
  <img src="https://img.shields.io/badge/InterviewPilot-AI%20面试准备平台-3b82f6?style=for-the-badge&logo=data:image/svg+xml;base64,..." alt="InterviewPilot" />
</p>

<p align="center">
  <strong>基于 RAG 架构的 AI 面试准备平台</strong><br/>
  简历解析 · 语义匹配 · 智能题库 · 模拟面试 · 四维评分 · STAR 复盘
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Vue%203-4FC08D?style=flat-square&logo=vue.js&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
</p>

---

## 功能全景

<table>
<tr>
<td width="50%">

### RAG 知识库
上传简历与 JD，自动解析 PDF / DOCX / PPTX / TXT，语义切片后通过 Embedding 存入 pgvector 向量库。后续所有问答均基于向量检索召回相关片段，告别"幻觉回答"。

### AI 四维评分
从 **表达清晰度 · 结构化程度 · 证据充分度 · 复盘深度** 四个维度对回答量化评分，由 LLM 结构化输出驱动，非随机数。

</td>
<td width="50%">

### 岗位匹配度计算
基于简历切片与 JD 关键点的语义相似度，动态计算 Fit Score，不再是固定值。

### STAR Feedback 复盘
每次模拟面试后自动生成结构化复盘报告，包含整体评价、维度分析、改进建议和行动计划。

</td>
</tr>
<tr>
<td>

### 智能追问
根据候选人上一轮回答动态生成追问，模拟真实面试中"深挖细节"的场景。

### 全局 AI 助手
随时唤醒的 AI 教练，引用简历、JD、面试记录和复盘报告作为上下文，提供针对性建议。

</td>
<td>

### SSE 流式输出
所有 AI 回答均通过 Server-Sent Events 流式推送，首字延迟低，体验流畅。

### 数据可视化
ECharts 驱动的雷达图与趋势图，直观展示能力维度分布和分数变化趋势。

</td>
</tr>
</table>

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 + TS)                        │
│  Pinia 状态管理 │ TanStack Query │ shadcn-vue 组件 │ ECharts   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + SSE
┌────────────────────────────┴────────────────────────────────────┐
│                      后端 (FastAPI + Python)                     │
│  JWT 鉴权 │ 结构化日志 │ 全局异常处理 │ 文件解析 Pipeline      │
├─────────────────────────────────────────────────────────────────┤
│                        AI Agent 层                              │
│  Chat Completions │ Streaming │ RAG 检索增强 │ 结构化输出      │
├─────────────────────────────────────────────────────────────────┤
│                     数据层 (PostgreSQL)                          │
│  用户 · 文档 · 切片 · 计划 · 题库 · 面试 · 报告 · 对话        │
│            pgvector 扩展 ── L2 / Cosine 向量检索                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/lanmao657/InterviewPilot-agent.git
cd InterviewPilot-agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 AI_API_KEY（兼容 OpenAI 接口的服务商均可）

# 3. 一键启动
docker compose up
```

浏览器访问 `http://localhost:5173`，后端健康检查 `http://localhost:8000/health`。

### 方式二：本地开发

**启动数据库**

```bash
docker compose up db
```

**启动后端**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**启动前端**

```bash
cd frontend
npm install
npm run dev
```

> 没有配置 `AI_API_KEY` 时，系统会使用本地模拟输出跑通完整流程，适合前端开发调试。

---

## 项目结构

```
InterviewPilot-agent/
├── backend/
│   ├── app/
│   │   ├── core/                # 基础设施
│   │   │   ├── config.py        #   环境变量与 Pydantic Settings
│   │   │   ├── database.py      #   SQLAlchemy 引擎与会话
│   │   │   ├── logging.py       #   structlog 结构化日志
│   │   │   └── security.py      #   JWT 签发与 bcrypt 哈希
│   │   ├── models/              # 数据模型
│   │   │   ├── domain.py        #   用户 · 文档 · 计划 · 题库 · 面试 · 报告 · 对话
│   │   │   └── document_chunk.py#   文档切片 + pgvector 向量
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py          #   注册 / 登录 / 游客 / 刷新令牌
│   │   │   ├── documents.py     #   文档上传与解析
│   │   │   ├── prep_plans.py    #   准备计划生成（含匹配度计算）
│   │   │   ├── questions.py     #   智能题库生成
│   │   │   ├── interviews.py    #   模拟面试与评分
│   │   │   ├── reports.py       #   STAR 复盘报告
│   │   │   ├── assistant.py     #   AI 助手对话
│   │   │   └── streams.py       #   SSE 流式接口
│   │   ├── services/            # 业务逻辑
│   │   │   ├── ai_agent.py      #   AI Agent（Chat + RAG + 流式）
│   │   │   ├── documents.py     #   文档解析 Pipeline
│   │   │   ├── embedding.py     #   Embedding + 文本切片
│   │   │   ├── matching.py      #   岗位匹配度计算
│   │   │   ├── retrieval.py     #   向量检索服务
│   │   │   └── assistant_*.py   #   助手上下文与历史管理
│   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   └── deps.py              # FastAPI 依赖注入
│   ├── alembic/                 # 数据库迁移
│   ├── tests/                   # 测试套件（36 个用例）
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               # 页面组件
│   │   │   ├── DashboardPage    #   仪表盘概览
│   │   │   ├── DocumentsPage    #   简历与 JD 管理
│   │   │   ├── QuestionsPage    #   题库生成与浏览
│   │   │   ├── InterviewPage    #   模拟面试
│   │   │   ├── AssistantPage    #   AI 助手
│   │   │   ├── ReportsPage      #   复盘报告与可视化
│   │   │   ├── SettingsPage     #   系统设置
│   │   │   └── LoginPage        #   登录 / 注册 / 游客
│   │   ├── components/
│   │   │   ├── layout/          #   AppShell 侧边栏 + 移动端适配
│   │   │   ├── charts/          #   ECharts 雷达图 / 趋势图
│   │   │   ├── assistant/       #   全局 AI 助手浮窗
│   │   │   └── ui/              #   shadcn-vue 风格组件库
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── lib/                 # API 客户端 + 工具函数
│   │   └── router.ts            # Vue Router 路由守卫
│   └── package.json
├── docker-compose.yml           # 一键部署
└── .github/workflows/ci.yml     # GitHub Actions CI
```

---

## 核心 API

| 方法 | 路径 | 功能 |
|------|------|------|
| `POST` | `/api/auth/register` | 用户注册 |
| `POST` | `/api/auth/login` | 用户登录 |
| `POST` | `/api/auth/guest` | 游客模式（免注册体验） |
| `POST` | `/api/documents/resume` | 上传简历 |
| `POST` | `/api/documents/job-description` | 上传 JD |
| `POST` | `/api/prep-plans` | 生成准备计划（含 Fit Score） |
| `POST` | `/api/questions/generate` | 生成智能题库 |
| `POST` | `/api/interviews` | 创建模拟面试 |
| `POST` | `/api/interviews/{id}/answer` | 提交回答并评分 |
| `POST` | `/api/reports/{id}` | 生成 STAR 复盘报告 |
| `GET`  | `/api/stream/assistant/chat` | SSE 流式 AI 助手 |
| `GET`  | `/api/stream/interviews/{id}/follow-up` | SSE 流式追问 |

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接地址 | `postgresql+psycopg://...localhost:5432/interviewpilot` |
| `JWT_SECRET` | JWT 签名密钥 | `change-me-in-production` |
| `AI_BASE_URL` | OpenAI 兼容接口地址 | `https://api.openai.com/v1` |
| `AI_API_KEY` | 模型服务密钥 | 空（使用本地模拟） |
| `AI_MODEL` | 模型名称 | `gpt-4.1-mini` |
| `EMBEDDING_MODEL` | 向量模型 | `text-embedding-3-small` |
| `CORS_ORIGINS` | 允许的前端来源 | localhost:5173-5174 |

---

## 测试

```bash
# 后端测试（36 个用例）
cd backend
pytest -v

# 前端类型检查
cd frontend
npx vue-tsc --noEmit

# 前端构建验证
cd frontend
npm run build
```

---

## 技术亮点

- **RAG Pipeline** — 文档解析 → 语义切片（段落 + 句子 + 重叠窗口） → Embedding 向量化 → pgvector L2/Cosine 检索 → 上下文注入
- **四维评分体系** — LLM 结构化输出 `{clarity, structure, evidence, reflection}`，非硬编码随机数
- **动态匹配度** — 简历切片与 JD 关键点逐一做语义检索，取最大相似度均值映射为 0-100 分
- **流式架构** — FastAPI `StreamingResponse` + SSE，前端 `ReadableStream` 实时渲染
- **多格式解析** — 统一 Pipeline 支持 PDF（pypdf）、DOCX（python-docx）、PPTX（python-pptx）、纯文本
- **玻璃态 UI** — Glassmorphism 设计语言，支持深色/浅色/跟随系统三种主题，图表组件自动适配主题
- **移动适配** — 响应式侧边栏 + 底部导航栏，支持手机端完整使用
- **面试题库交互** — 侧边栏题库选择面板，支持回答字数统计、进度追踪、追问引用
- **结构化报告** — 复盘报告自动格式化为分段文本（整体评价 / 维度评分 / 改进建议 / 行动计划）
- **游客模式保护** — 退出游客模式时弹出确认对话框，防止数据意外丢失

---

## 更新日志

---

## 更新日志

### 2026-05-30 Phase 1：关键 Bug 修复

- **修复报告内容 JSON 显示**：复盘报告从原始 JSON 改为结构化分段文本（整体评价 / 维度评分 / 改进建议 / 行动计划）
- **统一雷达图维度标签**：后端 metrics key 统一为 `clarity` / `structure` / `evidence` / `reflection`，与雷达图标签语义一致
- **图表主题适配**：雷达图和趋势图自动响应深色/浅色主题切换，轴文字、网格线、配色全部适配
- **面试页流程增强**：新增题库选择侧边栏、回答字数统计、已答题进度条、追问引用按钮
- **游客模式保护**：退出时弹出确认对话框，DashboardPage 新增注册引导卡片

---

## License

MIT
