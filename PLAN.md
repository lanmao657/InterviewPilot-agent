# InterviewPilot 改进实施计划

## Context

当前项目是一个 AI 面试准备平台的原型，存在以下核心问题使其无法写进简历：
- AI 调用只有 `chat/completions`，无 RAG/Embedding/向量检索
- 评分是假的：`min(95, max(45, 55 + len(answer) // 18))`（`ai_agent.py:92`）
- 题库是硬编码 6 个模板循环（`ai_agent.py:71-88`）
- Fit Score 是固定值 78/68（`prep_plans.py:30`）
- 报告 metrics 是硬编码 dict（`reports.py:36`）
- 文档摘要不是 AI 生成的（`documents.py:22-34`）
- 测试只有 2 个，无 CI/CD，无日志

改进目标：让项目具备 **RAG pipeline + 真正的 AI 评分 + 工程化实践**，可以在简历上展示为一个有技术深度的 AI 应用项目。

---

## 阶段一：RAG 知识库 + 向量检索（核心卖点，约 3-4 天）

### Step 1.1: 引入 pgvector + Embedding 存储

**改动文件：**
- `docker-compose.yml` — 使用 `pgvector/pgvector:pg17` 替换 `postgres:17`
- `backend/requirements.txt` — 新增 `pgvector`, `openai`（用于 embedding）
- `backend/app/core/config.py` — 新增 `embedding_model`, `embedding_dimensions` 配置
- `backend/app/models/domain.py` — 新增 `DocumentChunk` 模型
- `backend/alembic/versions/` — 新增 migration

**具体改动：**

```python
# models/domain.py 新增
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list] = mapped_column(Vector(1536))  # pgvector
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped[Document] = relationship()
```

**为什么：** pgvector 是最轻量的向量方案，不需要额外引入 Milvus/Qdrant，与现有 PostgreSQL 一体部署。1536 维是 `text-embedding-3-small` 的默认维度。

**好处：** 简历上可以写"基于 pgvector 实现文档向量存储与语义检索"。

### Step 1.2: 文档切片 + Embedding Pipeline

**改动文件：**
- `backend/app/services/documents.py` — 重构 `summarize_document`，新增 `chunk_text` 和 `embed_chunks`
- `backend/app/services/embedding.py` — 新建，封装 Embedding API 调用
- `backend/app/routers/documents.py` — 上传后自动触发切片+向量化

**具体逻辑：**

```
上传 PDF/DOCX → extract_upload_text() → chunk_text(按段落/512 token 切片)
→ embed_chunks() → 存入 document_chunks 表 → 同时用 LLM 生成结构化摘要
```

```python
# services/embedding.py
class EmbeddingService:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """调用 OpenAI Embedding API，返回向量列表"""
        ...

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """按段落 + token 限制切片，带重叠"""
        ...
```

**为什么：** 切片是 RAG 的基础。不切片就无法精准检索，整段塞进 prompt 会超出 context window 且浪费 token。overlap 确保上下文连贯。

**好处：** 展示你理解 RAG pipeline 的完整链路：切片 → 向量化 → 存储 → 检索。

### Step 1.3: 语义检索 + RAG 增强问答

**改动文件：**
- `backend/app/services/ai_agent.py` — 重构 `_chat` 和 `stream_chat`，新增 RAG 检索
- `backend/app/services/retrieval.py` — 新建，封装向量检索逻辑
- `backend/app/routers/interviews.py` — 回答时注入检索上下文
- `backend/app/routers/questions.py` — 生成题目时注入简历/JD 上下文
- `backend/app/routers/prep_plans.py` — 生成计划时注入检索上下文

**具体逻辑：**

```python
# services/retrieval.py
class RetrievalService:
    async def search(self, query: str, user_id: int, top_k: int = 5) -> list[str]:
        """1. 对 query 做 embedding
           2. 在 document_chunks 中做 cosine similarity 检索
           3. 返回 top_k 相关片段"""
        ...

# services/ai_agent.py 改造
async def _chat_with_rag(self, system: str, user: str, user_id: int) -> str:
    relevant_chunks = await RetrievalService().search(user, user_id, top_k=3)
    context = "\n---\n".join(relevant_chunks)
    enriched_system = f"{system}\n\n以下是候选人的相关资料：\n{context}"
    return await self._chat(enriched_system, user)
```

**为什么：** RAG 的核心价值是"让 AI 基于用户的真实资料回答"，而不是泛泛而谈。面试评分、题目生成、路线规划都应该基于简历和 JD 的具体内容。

**好处：** 简历上可以写"实现基于 RAG 的智能问答，通过向量检索提升回答准确率"。

### Step 1.4: Fit Score 语义匹配计算

**改动文件：**
- `backend/app/services/matching.py` — 新建
- `backend/app/routers/prep_plans.py` — 用真实匹配度替换固定值

**具体逻辑：**

```python
# services/matching.py
class MatchingService:
    async def compute_fit_score(self, resume_id: int, jd_id: int, user_id: int) -> int:
        """1. 分别获取简历和 JD 的所有 chunks
           2. 对 JD 每个 chunk，在简历 chunks 中做语义检索
           3. 计算平均相似度 → 映射到 0-100 分"""
        ...
```

**为什么：** 现在 `fit_score=78 if resume and jd else 68`（`prep_plans.py:30`）是假的。真实的匹配度计算是这个产品的核心价值。

**好处：** 展示"基于向量相似度的岗位匹配算法"，面试官可以直接问你实现细节。

---

## 阶段二：真正的 AI 评分和追问（约 2-3 天）

### Step 2.1: LLM 结构化评分

**改动文件：**
- `backend/app/services/ai_agent.py` — 重写 `score_answer`
- `backend/app/schemas.py` — 新增评分相关的 response schema

**具体改动：**

```python
# ai_agent.py 重写 score_answer
async def score_answer(self, question: str, answer: str, user_id: int) -> dict:
    system = """你是一位资深面试官，请从以下4个维度对候选人的回答评分（0-100）：
- clarity: 表达清晰度
- structure: 结构化程度（STAR）
- evidence: 证据和数据充分度
- reflection: 复盘和反思深度

严格按 JSON 格式输出：
{"score": 总分, "dimensions": {"clarity": 分, "structure": 分, "evidence": 分, "reflection": 分}, "summary": "一句话总结", "strengths": ["优点1"], "improvements": ["改进1"], "follow_up": "追问"}"""

    result = await self._chat_with_rag(system, f"题目：{question}\n回答：{answer}", user_id)
    return json.loads(result)  # 使用 JSON mode 或 structured output
```

**为什么：** 现在的评分是 `len(answer) // 18`，答案越长分越高，完全没有实际意义。LLM 结构化输出是 prompt engineering 的核心技能。

**好处：** 简历上可以写"设计多维度 AI 评分体系，通过结构化 Prompt 实现量化评估"。

### Step 2.2: AI 动态追问

**改动文件：**
- `backend/app/services/ai_agent.py` — 新增 `generate_follow_up` 方法
- `backend/app/routers/streams.py` — 追问使用 RAG 上下文

**具体逻辑：**

追问不再是固定模板，而是：
1. 分析上一轮回答的薄弱点
2. 检索简历中相关经历
3. 生成有针对性的深挖问题

**为什么：** 真实面试中面试官会根据回答追问。固定追问没有训练价值。

### Step 2.3: LLM 驱动的题目生成

**改动文件：**
- `backend/app/services/ai_agent.py` — 重写 `generate_questions`

**具体改动：**

```python
async def generate_questions(self, focus: str, count: int, user_id: int) -> list[dict]:
    system = f"""你是面试题设计专家。根据候选人的简历和 JD，生成 {count} 道面试题。
每道题包含：category, difficulty(easy/medium/hard), prompt, rubric(评分标准)。
输出 JSON 数组。"""
    result = await self._chat_with_rag(system, f"训练重点：{focus}", user_id)
    return json.loads(result)
```

**为什么：** 现在是 6 个硬编码模板循环（`ai_agent.py:71-88`），没有实际价值。

---

## 阶段三：报告增强 + 前端可视化（约 2-3 天）

### Step 3.1: AI 驱动的复盘报告

**改动文件：**
- `backend/app/services/ai_agent.py` — 重写 `build_report`，输出结构化报告
- `backend/app/routers/reports.py` — metrics 从 AI 输出获取（替换硬编码）
- `backend/app/schemas.py` — 新增 ReportMetrics schema

**具体改动：**

```python
# reports.py 当前问题（第36行）：
metrics={"表达结构": 78, "岗位匹配": 82, "证据质量": 74, "复盘深度": 76}  # 硬编码！

# 改为从 AI 输出的每轮 dimensions 聚合
```

**为什么：** 报告的 metrics 是假数据，面试官一问就穿帮。

### Step 3.2: 报告可视化（前端 ECharts）

**改动文件：**
- `frontend/package.json` — 新增 `echarts` + `vue-echarts`
- `frontend/src/components/charts/` — 新建图表组件目录
- `frontend/src/components/charts/RadarChart.vue` — 能力雷达图
- `frontend/src/components/charts/TrendChart.vue` — 分数趋势图
- `frontend/src/pages/ReportsPage.vue` — 集成图表

**具体改动：**

- 报告页展示能力雷达图（clarity/structure/evidence/reflection 四维度）
- 展示多轮面试的分数趋势折线图
- STAR 结构分析的可视化

**为什么：** 数据可视化让项目从"能用"变成"好看"。截图放简历上更有说服力。

**好处：** 简历上可以写"使用 ECharts 实现面试能力多维度可视化分析"。

### Step 3.3: Dashboard 增强

**改动文件：**
- `frontend/src/pages/DashboardPage.vue` — 增加统计图表和最近面试概览

**具体改动：**
- 增加"最近面试趋势"折线图
- 增加"能力维度"雷达图
- 增加"待办事项"（未完成的准备计划、未练习的题目）

---

## 阶段四：工程化补齐（约 2-3 天）

### Step 4.1: 结构化日志 + 错误处理

**改动文件：**
- `backend/requirements.txt` — 新增 `structlog`
- `backend/app/core/logging.py` — 新建，配置结构化日志
- `backend/app/main.py` — 添加全局异常处理中间件
- `backend/app/services/ai_agent.py` — 添加重试/超时/降级策略

**具体改动：**

```python
# core/logging.py
import structlog
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
)
logger = structlog.get_logger()

# services/ai_agent.py 添加重试
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
async def _chat(self, system: str, user: str) -> str:
    ...
```

**为什么：** 面试官会问"AI 调用失败了怎么办？"。你需要能回答重试、降级、超时策略。

**好处：** 展示生产环境思维。

### Step 4.2: 测试覆盖

**改动文件：**
- `backend/tests/test_documents.py` — 新建
- `backend/tests/test_prep_plans.py` — 新建
- `backend/tests/test_interviews.py` — 新建
- `backend/tests/test_questions.py` — 新建
- `backend/tests/test_reports.py` — 新建
- `backend/tests/test_matching.py` — 新建
- `backend/tests/conftest.py` — 新建，共享 fixture
- `frontend/src/components/layout/AppShell.test.ts` — 已有
- `frontend/src/pages/LoginPage.test.ts` — 已有

**具体改动：**

```python
# tests/conftest.py
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_header(client):
    client.post("/api/auth/register", json={...})
    token = client.post("/api/auth/login", json={...}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# tests/test_interviews.py
def test_answer_and_score(client, auth_header):
    """测试回答后返回结构化评分"""
    interview = client.post("/api/interviews", json={...}, headers=auth_header).json()
    result = client.post(f"/api/interviews/{interview['id']}/answer",
        json={"question": "...", "answer": "..."}, headers=auth_header)
    assert result.status_code == 200
    turn = result.json()["turns"][-1]
    assert "dimensions" in turn["feedback"]
    assert 0 <= turn["score"] <= 100
```

**为什么：** 当前只有 2 个测试（`test_auth.py` 和 `test_ai_agent.py`）。测试覆盖是工程化的基本功。

### Step 4.3: CI/CD Pipeline

**改动文件：**
- `.github/workflows/ci.yml` — 新建
- `backend/Dockerfile` — 新建，多阶段构建
- `frontend/Dockerfile` — 新建，多阶段构建
- `docker-compose.yml` — 更新，使用本地 Dockerfile

**具体改动：**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest -v
      - run: cd backend && ruff check .

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - run: cd frontend && npm ci && npm run build && npm test
```

**为什么：** 没有 CI/CD 的项目在简历上说服力减半。

**好处：** 简历上可以写"配置 GitHub Actions CI/CD，实现自动化测试与构建"。

### Step 4.4: LLM Provider 抽象层

**改动文件：**
- `backend/app/services/llm_provider.py` — 新建
- `backend/app/services/ai_agent.py` — 使用 provider 抽象
- `backend/app/core/config.py` — 新增 `llm_provider` 配置项

**具体改动：**

```python
# services/llm_provider.py
class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], model: str) -> str: ...

    @abstractmethod
    async def stream(self, messages: list[dict], model: str) -> AsyncGenerator[str, None]: ...

class OpenAIProvider(LLMProvider):
    async def chat(self, messages, model): ...

class AnthropicProvider(LLMProvider):
    async def chat(self, messages, model): ...
```

**为什么：** 展示你理解 LLM 生态的多样性，支持多模型是 AI 应用的基本架构能力。

---

## 阶段五：产品增强（约 2-3 天）

### Step 5.1: 语音输入

**改动文件：**
- `frontend/src/composables/useSpeechRecognition.ts` — 新建
- `frontend/src/pages/InterviewPage.vue` — 集成语音输入
- `backend/requirements.txt` — 新增 `openai-whisper`（可选后端转写）

**具体改动：**

```typescript
// composables/useSpeechRecognition.ts
export function useSpeechRecognition() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
  // ... 实现语音转文字
}
```

**为什么：** 真实面试是口述的，打字模拟体验差。语音能力展示端到端产品思维。

### Step 5.2: PDF 报告导出

**改动文件：**
- `backend/requirements.txt` — 新增 `weasyprint` 或 `reportlab`
- `backend/app/routers/reports.py` — 新增导出端点
- `frontend/src/pages/ReportsPage.vue` — 添加导出按钮

**为什么：** 可导出的报告增加了产品的实用性，也方便面试官审阅。

### Step 5.3: 前端设置页完善

**改动文件：**
- `frontend/src/pages/SettingsPage.vue` — 完善模型选择、个人信息编辑

---

## 实施顺序总结

```
阶段一 (RAG):     Step 1.1 → 1.2 → 1.3 → 1.4    [核心卖点，优先做]
阶段二 (AI评分):  Step 2.1 → 2.2 → 2.3            [紧随 RAG 之后]
阶段三 (可视化):  Step 3.1 → 3.2 → 3.3            [让项目"好看"]
阶段四 (工程化):  Step 4.1 → 4.2 → 4.3 → 4.4     [补齐基本功]
阶段五 (增强):    Step 5.1 → 5.2 → 5.3            [锦上添花]
```

## 改进后简历描述

> **InterviewPilot — AI 面试准备平台** | [GitHub 链接]
> - 基于 RAG 架构实现简历/JD 语义匹配与智能问答，使用 pgvector + Embedding 构建向量检索 pipeline
> - 设计四维度 AI 评分体系（清晰度/结构化/证据/复盘），通过 LLM 结构化输出实现量化评估
> - 构建文档解析 Pipeline，支持 PDF/DOCX 结构化提取、语义切片与岗位匹配度计算
> - 使用 FastAPI + Vue 3 + PostgreSQL 全栈开发，集成 GitHub Actions CI/CD + Docker 容器化部署
> - 实现 SSE 流式输出、语音输入、ECharts 数据可视化，优化面试模拟体验

## 验证方式

1. **RAG 验证：** 上传一份简历 → 提问"我在 XX 项目中用了什么技术" → 验证回答基于简历内容
2. **评分验证：** 提交一段回答 → 验证返回结构化评分 JSON（四维度分数 + 反馈）
3. **匹配度验证：** 上传简历+JD → 验证 Fit Score 不再是固定值
4. **测试验证：** `cd backend && pytest -v` 全部通过
5. **CI 验证：** push 到 GitHub 后 Actions 自动运行
6. **可视化验证：** 生成报告后查看雷达图和趋势图
