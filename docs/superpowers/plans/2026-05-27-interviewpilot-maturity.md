# InterviewPilot 成熟度提升实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 InterviewPilot 从原型升级为具备 RAG pipeline、真正 AI 评分、工程化实践的成熟项目

**Architecture:** 基于 pgvector 实现向量检索，使用结构化 Prompt 实现 AI 评分，通过 FastAPI + Vue 3 + PostgreSQL 构建全栈应用

**Tech Stack:** FastAPI, Vue 3, PostgreSQL, pgvector, OpenAI API, ECharts, Docker, GitHub Actions

---

## 文件结构映射

### 后端新增文件
- `backend/app/models/document_chunk.py` — 文档切片模型
- `backend/app/services/embedding.py` — Embedding 服务
- `backend/app/services/retrieval.py` — 向量检索服务
- `backend/app/services/matching.py` — 匹配度计算服务
- `backend/app/services/llm_provider.py` — LLM 提供者抽象层
- `backend/app/core/logging.py` — 结构化日志配置
- `backend/app/schemas/evaluation.py` — 评分相关 schema
- `backend/app/schemas/report.py` — 报告相关 schema
- `backend/tests/conftest.py` — 测试配置
- `backend/tests/test_documents.py` — 文档测试
- `backend/tests/test_interviews.py` — 面试测试
- `backend/tests/test_matching.py` — 匹配度测试

### 后端修改文件
- `docker-compose.yml` — 使用 pgvector 镜像
- `backend/requirements.txt` — 新增依赖
- `backend/app/core/config.py` — 新增配置项
- `backend/app/models/domain.py` — 新增 DocumentChunk 模型
- `backend/app/services/ai_agent.py` — 重构 AI 服务
- `backend/app/services/documents.py` — 增强文档处理
- `backend/app/routers/documents.py` — 增强文档路由
- `backend/app/routers/interviews.py` — 增强面试路由
- `backend/app/routers/reports.py` — 增强报告路由
- `backend/app/routers/prep_plans.py` — 增强计划路由

### 前端新增文件
- `frontend/src/components/charts/RadarChart.vue` — 雷达图组件
- `frontend/src/components/charts/TrendChart.vue` — 趋势图组件
- `frontend/src/composables/useSpeechRecognition.ts` — 语音识别

### 前端修改文件
- `frontend/package.json` — 新增 ECharts 依赖
- `frontend/src/pages/ReportsPage.vue` — 集成图表
- `frontend/src/pages/DashboardPage.vue` — 增强仪表盘
- `frontend/src/pages/InterviewPage.vue` — 集成语音输入

### CI/CD 新增文件
- `.github/workflows/ci.yml` — GitHub Actions 配置
- `backend/Dockerfile` — 后端 Docker 配置
- `frontend/Dockerfile` — 前端 Docker 配置

---

## 阶段一：RAG 知识库 + 向量检索（核心卖点）

### Task 1.1: 配置 pgvector 环境

**Files:**
- Modify: `docker-compose.yml:1-48`
- Modify: `backend/requirements.txt:1-16`
- Modify: `backend/app/core/config.py`

- [ ] **Step 1: 更新 docker-compose.yml 使用 pgvector**

```yaml
services:
  db:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: interviewpilot
      POSTGRES_PASSWORD: interviewpilot
      POSTGRES_DB: interviewpilot
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U interviewpilot -d interviewpilot"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    image: python:3.11-slim
    working_dir: /app/backend
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+psycopg://interviewpilot:interviewpilot@db:5432/interviewpilot
    command: sh -c "pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

  frontend:
    image: node:24-alpine
    working_dir: /app/frontend
    volumes:
      - .:/app
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres-data:
```

- [ ] **Step 2: 更新 requirements.txt 添加依赖**

```txt
alembic==1.17.2
bcrypt==4.1.3
email-validator==2.3.0
fastapi==0.125.0
httpx==0.28.1
openai==1.61.0
passlib[bcrypt]==1.7.4
pgvector==0.3.6
psycopg[binary]==3.3.2
pydantic-settings==2.12.0
pytest==9.0.2
python-docx==1.2.0
python-jose[cryptography]==3.5.0
python-multipart==0.0.20
pypdf==6.4.1
SQLAlchemy==2.0.45
uvicorn[standard]==0.38.0
```

- [ ] **Step 3: 更新 config.py 添加 Embedding 配置**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 现有配置
    database_url: str = "postgresql+psycopg://interviewpilot:interviewpilot@localhost:5432/interviewpilot"
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4"
    secret_key: str = "change-me-in-production"

    # Embedding 配置
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: 验证配置**

Run: `cd backend && python -c "from app.core.config import get_settings; print(get_settings().embedding_model)"`
Expected: `text-embedding-3-small`

- [ ] **Step 5: 提交更改**

```bash
git add docker-compose.yml backend/requirements.txt backend/app/core/config.py
git commit -m "feat: configure pgvector environment and embedding settings"
```

---

### Task 1.2: 创建 DocumentChunk 模型

**Files:**
- Create: `backend/app/models/document_chunk.py`
- Modify: `backend/app/models/domain.py`
- Create: `backend/alembic/versions/xxx_add_document_chunks.py`

- [ ] **Step 1: 创建 DocumentChunk 模型文件**

```python
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document = relationship("Document", back_populates="chunks")
```

- [ ] **Step 2: 更新 domain.py 导入模型**

```python
# 在文件末尾添加
from app.models.document_chunk import DocumentChunk
```

- [ ] **Step 3: 生成 Alembic 迁移**

Run: `cd backend && alembic revision --autogenerate -m "add_document_chunks_table"`
Expected: `Generating alembic/versions/xxx_add_document_chunks.py`

- [ ] **Step 4: 应用迁移**

Run: `cd backend && alembic upgrade head`
Expected: `Running upgrade -> xxx_add_document_chunks`

- [ ] **Step 5: 验证表创建**

Run: `docker exec -it interviewpilot-db-1 psql -U interviewpilot -d interviewpilot -c "\dt"`
Expected: 显示 `document_chunks` 表

- [ ] **Step 6: 提交更改**

```bash
git add backend/app/models/document_chunk.py backend/app/models/domain.py backend/alembic/versions/
git commit -m "feat: add DocumentChunk model with pgvector support"
```

---

### Task 1.3: 实现 Embedding 服务

**Files:**
- Create: `backend/app/services/embedding.py`
- Create: `backend/tests/test_embedding.py`

- [ ] **Step 1: 编写失败的测试**

```python
# backend/tests/test_embedding.py
import pytest
from app.services.embedding import EmbeddingService


@pytest.fixture
def embedding_service():
    return EmbeddingService()


def test_chunk_text_short_text(embedding_service):
    """测试短文本不需要切片"""
    text = "这是一段短文本"
    chunks = embedding_service.chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long_text(embedding_service):
    """测试长文本正确切片"""
    text = "这是第一段内容。\n\n这是第二段内容。\n\n这是第三段内容。"
    chunks = embedding_service.chunk_text(text, chunk_size=20)
    assert len(chunks) > 1
    assert all(len(chunk) <= 25 for chunk in chunks)  # 允许一定误差


def test_chunk_text_overlap(embedding_service):
    """测试切片有重叠"""
    text = "A" * 100
    chunks = embedding_service.chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 2
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_embedding.py -v`
Expected: `FAIL` with `ModuleNotFoundError: No module named 'app.services.embedding'`

- [ ] **Step 3: 实现 EmbeddingService**

```python
# backend/app/services/embedding.py
import openai
from app.core.config import get_settings


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.ai_api_key)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """调用 OpenAI Embedding API，返回向量列表"""
        response = await self.client.embeddings.create(
            model=self.settings.embedding_model,
            input=texts,
            dimensions=self.settings.embedding_dimensions,
        )
        return [item.embedding for item in response.data]

    def chunk_text(
        self, text: str, chunk_size: int = 512, overlap: int = 64
    ) -> list[str]:
        """按段落 + token 限制切片，带重叠"""
        # 先按段落分割
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # 如果当前段落太长，按句子分割
            if len(paragraph) > chunk_size:
                sentences = paragraph.replace("。", "。\n").split("\n")
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # 保留重叠部分
                            overlap_text = current_chunk[-overlap:] if overlap else ""
                            current_chunk = overlap_text + sentence
                        else:
                            current_chunk = sentence
                    else:
                        current_chunk += "\n" + sentence if current_chunk else sentence
            else:
                if len(current_chunk) + len(paragraph) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        overlap_text = current_chunk[-overlap:] if overlap else ""
                        current_chunk = overlap_text + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd backend && pytest tests/test_embedding.py -v`
Expected: `PASSED`

- [ ] **Step 5: 提交更改**

```bash
git add backend/app/services/embedding.py backend/tests/test_embedding.py
git commit -m "feat: implement EmbeddingService with chunking logic"
```

---

### Task 1.4: 实现向量检索服务

**Files:**
- Create: `backend/app/services/retrieval.py`
- Create: `backend/tests/test_retrieval.py`

- [ ] **Step 1: 编写失败的测试**

```python
# backend/tests/test_retrieval.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.retrieval import RetrievalService


@pytest.fixture
def mock_embedding_service():
    service = AsyncMock()
    service.embed.return_value = [[0.1] * 1536]
    return service


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def retrieval_service(mock_embedding_service, mock_db):
    return RetrievalService(mock_embedding_service, mock_db)


@pytest.mark.asyncio
async def test_search_returns_chunks(retrieval_service, mock_embedding_service):
    """测试检索返回相关切片"""
    # 模拟数据库查询结果
    mock_chunk = MagicMock()
    mock_chunk.content = "测试内容"
    mock_chunk.embedding = [0.1] * 1536

    retrieval_service.db.execute.return_value.scalars.return_value.all.return_value = [
        mock_chunk
    ]

    results = await retrieval_service.search("测试查询", user_id=1, top_k=3)

    assert len(results) > 0
    assert results[0] == "测试内容"
    mock_embedding_service.embed.assert_called_once()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_retrieval.py -v`
Expected: `FAIL` with `ModuleNotFoundError: No module named 'app.services.retrieval'`

- [ ] **Step 3: 实现 RetrievalService**

```python
# backend/app/services/retrieval.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk
from app.services.embedding import EmbeddingService


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService, db: AsyncSession):
        self.embedding_service = embedding_service
        self.db = db

    async def search(
        self, query: str, user_id: int, top_k: int = 5
    ) -> list[str]:
        """1. 对 query 做 embedding
           2. 在 document_chunks 中做 cosine similarity 检索
           3. 返回 top_k 相关片段
        """
        # 1. 对查询文本做 embedding
        query_embedding = await self.embedding_service.embed([query])
        if not query_embedding:
            return []

        query_vector = query_embedding[0]

        # 2. 使用 pgvector 的 cosine distance 检索
        # 使用 L2 distance 作为相似度度量
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.embedding.l2_distance(query_vector))
            .limit(top_k)
        )

        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        # 3. 返回相关片段内容
        return [chunk.content for chunk in chunks]

    async def search_with_scores(
        self, query: str, user_id: int, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """返回相关片段及其相似度分数"""
        query_embedding = await self.embedding_service.embed([query])
        if not query_embedding:
            return []

        query_vector = query_embedding[0]

        # 使用 cosine similarity
        stmt = (
            select(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
            )
            .where(DocumentChunk.user_id == user_id)
            .order_by("distance")
            .limit(top_k)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # cosine_distance 返回 0-2，转换为 0-1 的相似度
        return [(chunk.content, 1 - distance) for chunk, distance in rows]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd backend && pytest tests/test_retrieval.py -v`
Expected: `PASSED`

- [ ] **Step 5: 提交更改**

```bash
git add backend/app/services/retrieval.py backend/tests/test_retrieval.py
git commit -m "feat: implement RetrievalService with vector search"
```

---

### Task 1.5: 重构文档服务支持切片和向量化

**Files:**
- Modify: `backend/app/services/documents.py`
- Modify: `backend/app/routers/documents.py`
- Create: `backend/tests/test_documents.py`

- [ ] **Step 1: 编写失败的测试**

```python
# backend/tests/test_documents.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.documents import DocumentService


@pytest.fixture
def mock_embedding_service():
    service = AsyncMock()
    service.embed.return_value = [[0.1] * 1536]
    service.chunk_text.return_value = ["chunk1", "chunk2"]
    return service


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def document_service(mock_embedding_service, mock_db):
    return DocumentService(mock_embedding_service, mock_db)


@pytest.mark.asyncio
async def test_process_document_creates_chunks(
    document_service, mock_embedding_service, mock_db
):
    """测试文档处理创建切片"""
    # 模拟文档对象
    mock_document = MagicMock()
    mock_document.id = 1
    mock_document.user_id = 1
    mock_document.content = "测试文档内容"

    # 模拟数据库操作
    mock_db.get.return_value = mock_document

    await document_service.process_document(1)

    # 验证调用了切片和 embedding
    mock_embedding_service.chunk_text.assert_called_once()
    mock_embedding_service.embed.assert_called_once()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_documents.py -v`
Expected: `FAIL` with `ModuleNotFoundError: No module named 'app.services.documents'` (需要重命名)

- [ ] **Step 3: 重构 documents.py 服务**

```python
# backend/app/services/documents.py
from io import BytesIO

from docx import Document as DocxDocument
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding import EmbeddingService


async def extract_upload_text(file: UploadFile) -> str:
    data = await file.read()
    filename = file.filename or "uploaded-file"
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if suffix == "pdf":
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix == "docx":
        doc = DocxDocument(BytesIO(data))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    return data.decode("utf-8", errors="ignore").strip()


class DocumentService:
    def __init__(self, embedding_service: EmbeddingService, db: AsyncSession):
        self.embedding_service = embedding_service
        self.db = db

    async def process_document(self, document_id: int) -> None:
        """处理文档：切片 + 向量化"""
        # 获取文档
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            return

        # 切片
        chunks = self.embedding_service.chunk_text(document.content)

        # 生成 embeddings
        embeddings = await self.embedding_service.embed(chunks)

        # 保存切片到数据库
        for i, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=document_id,
                user_id=document.user_id,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding,
            )
            self.db.add(chunk)

        await self.db.commit()

    async def summarize_document(self, text: str, kind: str) -> dict:
        """生成文档摘要"""
        compact = " ".join(text.split())[:600]
        if kind == "resume":
            return {
                "type": "简历",
                "highlights": ["项目经历", "核心技能", "过往职责"],
                "preview": compact or "未解析到文本，请检查文件内容。",
            }
        return {
            "type": "JD",
            "highlights": ["岗位职责", "能力要求", "面试关注点"],
            "preview": compact or "未解析到文本，请检查文件内容。",
        }
```

- [ ] **Step 4: 更新文档路由**

```python
# backend/app/routers/documents.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.embedding import EmbeddingService
from app.services.documents import DocumentService, extract_upload_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    kind: str = "resume",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 提取文本
    content = await extract_upload_text(file)

    # 保存文档记录
    from app.models.document import Document

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        kind=kind,
        content=content,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # 异步处理切片和向量化
    embedding_service = EmbeddingService()
    document_service = DocumentService(embedding_service, db)
    await document_service.process_document(document.id)

    # 生成摘要
    summary = await document_service.summarize_document(content, kind)

    return {
        "id": document.id,
        "filename": file.filename,
        "kind": kind,
        "summary": summary,
    }
```

- [ ] **Step 5: 运行测试验证通过**

Run: `cd backend && pytest tests/test_documents.py -v`
Expected: `PASSED`

- [ ] **Step 6: 提交更改**

```bash
git add backend/app/services/documents.py backend/app/routers/documents.py backend/tests/test_documents.py
git commit -m "feat: refactor document service with chunking and vectorization"
```

---

### Task 1.6: 实现 RAG 增强的 AI 代理

**Files:**
- Modify: `backend/app/services/ai_agent.py`
- Create: `backend/tests/test_ai_agent_rag.py`

- [ ] **Step 1: 编写失败的测试**

```python
# backend/tests/test_ai_agent_rag.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ai_agent import AIAgent


@pytest.fixture
def mock_retrieval_service():
    service = AsyncMock()
    service.search.return_value = ["相关内容1", "相关内容2"]
    return service


@pytest.fixture
def ai_agent(mock_retrieval_service):
    agent = AIAgent()
    agent.retrieval_service = mock_retrieval_service
    return agent


@pytest.mark.asyncio
async def test_chat_with_rag_includes_context(ai_agent, mock_retrieval_service):
    """测试 RAG 聊天包含检索上下文"""
    with patch.object(ai_agent, '_chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "测试回答"

        result = await ai_agent._chat_with_rag("系统提示", "用户问题", user_id=1)

        # 验证调用了检索
        mock_retrieval_service.search.assert_called_once_with("用户问题", 1, top_k=3)

        # 验证系统提示包含检索内容
        call_args = mock_chat.call_args
        system_prompt = call_args[0][0]
        assert "相关内容1" in system_prompt
        assert "相关内容2" in system_prompt


@pytest.mark.asyncio
async def test_score_answer_returns_structured(ai_agent):
    """测试评分返回结构化结果"""
    with patch.object(ai_agent, '_chat_with_rag', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = '{"score": 85, "dimensions": {"clarity": 80, "structure": 85, "evidence": 90, "reflection": 85}, "summary": "回答优秀", "strengths": ["结构清晰"], "improvements": ["可以更具体"], "follow_up": "能否举例说明？"}'

        result = await ai_agent.score_answer("测试问题", "测试回答", user_id=1)

        assert result["score"] == 85
        assert "dimensions" in result
        assert len(result["dimensions"]) == 4
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_ai_agent_rag.py -v`
Expected: `FAIL` with `AttributeError: 'AIAgent' object has no attribute '_chat_with_rag'`

- [ ] **Step 3: 重构 ai_agent.py**

```python
# backend/app/services/ai_agent.py
import json
from collections.abc import AsyncGenerator
from typing import Optional

import httpx

from app.core.config import get_settings
from app.services.retrieval import RetrievalService


class AIAgent:
    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.settings = get_settings()
        self.retrieval_service = retrieval_service

    async def _chat(self, system: str, user: str) -> str:
        if not self.settings.ai_api_key:
            return self._fallback(system, user)

        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        }
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_with_rag(self, system: str, user: str, user_id: int) -> str:
        """带 RAG 上下文的聊天"""
        context = ""
        if self.retrieval_service:
            relevant_chunks = await self.retrieval_service.search(
                user, user_id, top_k=3
            )
            if relevant_chunks:
                context = "\n---\n".join(relevant_chunks)

        enriched_system = system
        if context:
            enriched_system = f"{system}\n\n以下是候选人的相关资料：\n{context}"

        return await self._chat(enriched_system, user)

    async def stream_chat(self, system: str, user: str) -> AsyncGenerator[str, None]:
        if not self.settings.ai_api_key:
            for chunk in self._fallback(system, user).split("，"):
                if chunk:
                    yield chunk + "，"
            return

        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line.removeprefix("data: ")
                    if raw == "[DONE]":
                        break
                    delta = json.loads(raw)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta

    async def generate_questions(
        self, focus: str, count: int, user_id: int
    ) -> list[dict]:
        """生成面试题（基于 RAG）"""
        system = f"""你是面试题设计专家。根据候选人的简历和 JD，生成 {count} 道面试题。
每道题包含：category, difficulty(easy/medium/hard), prompt, rubric(评分标准)。
输出 JSON 数组。"""

        result = await self._chat_with_rag(system, f"训练重点：{focus}", user_id)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # 降级到固定模板
            return self._fallback_questions(focus, count)

    async def score_answer(self, question: str, answer: str, user_id: int) -> dict:
        """评分回答（基于 RAG）"""
        system = """你是一位资深面试官，请从以下4个维度对候选人的回答评分（0-100）：
- clarity: 表达清晰度
- structure: 结构化程度（STAR）
- evidence: 证据和数据充分度
- reflection: 复盘和反思深度

严格按 JSON 格式输出：
{"score": 总分, "dimensions": {"clarity": 分, "structure": 分, "evidence": 分, "reflection": 分}, "summary": "一句话总结", "strengths": ["优点1"], "improvements": ["改进1"], "follow_up": "追问"}"""

        result = await self._chat_with_rag(
            system, f"题目：{question}\n回答：{answer}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_score()

    async def build_report(self, title: str, turns: list[dict], user_id: int) -> dict:
        """构建报告（基于 RAG）"""
        joined = "\n".join(
            f"Q:{turn['question']}\nA:{turn['answer']}" for turn in turns
        )

        system = """你是面试复盘教练，请输出中文 STAR Feedback 报告。
报告包含：
1. 整体评价
2. 各维度平均分（clarity, structure, evidence, reflection）
3. 改进建议
4. 下一步行动计划

输出 JSON 格式。"""

        result = await self._chat_with_rag(
            system, f"{title}\n{joined[:6000]}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_report(title, turns)

    async def build_roadmap(
        self, resume_text: str, jd_text: str, target_role: str, user_id: int
    ) -> dict:
        """构建路线图（基于 RAG）"""
        prompt = f"候选人简历：{resume_text[:2500]}\n岗位 JD：{jd_text[:2500]}\n目标岗位：{target_role}"
        content = await self._chat_with_rag(
            "你是中文 AI 面试教练，请输出简洁的准备路线。", prompt, user_id
        )
        return {
            "summary": content[:900],
            "milestones": ["岗位匹配分析", "高频题训练", "STAR 表达打磨", "模拟面试复盘"],
            "focusAreas": ["业务理解", "项目深挖", "结构化表达", "反问准备"],
        }

    async def coach_with_context(self, message: str, context: dict) -> str:
        return await self._chat(
            self.assistant_system_prompt(),
            self.assistant_user_prompt(message, context),
        )

    async def stream_coach_with_context(
        self, message: str, context: dict
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.stream_chat(
            self.assistant_system_prompt(),
            self.assistant_user_prompt(message, context),
        ):
            yield chunk

    def assistant_system_prompt(self) -> str:
        return (
            "你是 InterviewPilot 的 AI 面试准备教练。你只能围绕求职面试准备提供帮助："
            "简历与 JD 匹配、题库训练、模拟面试、STAR 表达、复盘报告和下一步行动。"
            "回答要具体、可执行、中文优先；如果上下文不足，引导用户上传简历与 JD。"
        )

    def assistant_user_prompt(self, message: str, context: dict) -> str:
        return f"用户问题：{message}\n\n当前用户上下文：\n{json.dumps(context, ensure_ascii=False, default=str)[:8000]}"

    def _fallback(self, system: str, user: str) -> str:
        return (
            "这是 InterviewPilot 的本地模拟 AI 输出。建议先上传简历与 JD，生成准备计划后再开始题库训练。"
            "如果已经有材料，可以优先选择 3 个最匹配岗位要求的项目，按 STAR 结构准备：背景、任务、行动、结果。"
            "下一步建议：补齐岗位信息、生成 6 道高频题、完成一轮文字模拟面试，并用复盘报告修正表达。"
        )

    def _fallback_questions(self, focus: str, count: int) -> list[dict]:
        prompts = [
            f"请结合 {focus} 讲一个最能体现你解决复杂问题的项目。",
            "如果面试官质疑你的项目影响力，你会如何用数据回应？",
            "描述一次你和团队意见不一致时的处理方式。",
            "请解释你最近一个项目中的关键技术或业务取舍。",
            "如果入职后 30 天内要交付结果，你会如何拆解计划？",
            "你有哪些短板？最近如何系统改进？",
        ]
        return [
            {
                "category": focus,
                "difficulty": "medium" if i % 3 else "hard",
                "prompt": prompts[i % len(prompts)],
                "rubric": {"clarity": 25, "structure": 25, "evidence": 25, "reflection": 25},
            }
            for i in range(count)
        ]

    def _fallback_score(self) -> dict:
        return {
            "score": 70,
            "dimensions": {
                "clarity": 70,
                "structure": 70,
                "evidence": 70,
                "reflection": 70,
            },
            "summary": "回答已覆盖核心问题，建议补充更明确的行动、量化结果和复盘。",
            "strengths": ["回答完整"],
            "improvements": ["可以更具体", "需要量化"],
            "follow_up": "能否补充一个具体指标？",
        }

    def _fallback_report(self, title: str, turns: list[dict]) -> dict:
        return {
            "title": title,
            "overall": "整体表现良好，建议加强结构化表达。",
            "average_scores": {
                "clarity": 75,
                "structure": 70,
                "evidence": 72,
                "reflection": 68,
            },
            "improvements": ["使用 STAR 结构", "补充量化数据", "加强复盘深度"],
            "next_steps": ["练习高频题", "准备项目案例", "模拟面试"],
        }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd backend && pytest tests/test_ai_agent_rag.py -v`
Expected: `PASSED`

- [ ] **Step 5: 提交更改**

```bash
git add backend/app/services/ai_agent.py backend/tests/test_ai_agent_rag.py
git commit -m "feat: refactor AIAgent with RAG support and structured scoring"
```

---

## 阶段二：AI 评分和追问

### Task 2.1: 实现匹配度计算服务

**Files:**
- Create: `backend/app/services/matching.py`
- Create: `backend/tests/test_matching.py`

- [ ] **Step 1: 编写失败的测试**

```python
# backend/tests/test_matching.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.matching import MatchingService


@pytest.fixture
def mock_retrieval_service():
    service = AsyncMock()
    service.search_with_scores.return_value = [
        ("简历内容1", 0.85),
        ("简历内容2", 0.72),
    ]
    return service


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def matching_service(mock_retrieval_service, mock_db):
    return MatchingService(mock_retrieval_service, mock_db)


@pytest.mark.asyncio
async def test_compute_fit_score(matching_service, mock_retrieval_service):
    """测试计算匹配度分数"""
    # 模拟 JD 文档
    mock_jd = MagicMock()
    mock_jd.content = "岗位要求：Python, FastAPI, PostgreSQL"

    # 模拟数据库查询
    matching_service.db.execute.return_value.scalar_one_or_none.return_value = mock_jd

    score = await matching_service.compute_fit_score(
        resume_id=1, jd_id=1, user_id=1
    )

    assert 0 <= score <= 100
    assert score > 70  # 应该有较高匹配度


@pytest.mark.asyncio
async def test_compute_fit_score_no_jd(matching_service):
    """测试没有 JD 时返回默认分数"""
    matching_service.db.execute.return_value.scalar_one_or_none.return_value = None

    score = await matching_service.compute_fit_score(
        resume_id=1, jd_id=1, user_id=1
    )

    assert score == 68  # 默认分数
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_matching.py -v`
Expected: `FAIL` with `ModuleNotFoundError: No module named 'app.services.matching'`

- [ ] **Step 3: 实现 MatchingService**

```python
# backend/app/services/matching.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.services.retrieval import RetrievalService


class MatchingService:
    def __init__(self, retrieval_service: RetrievalService, db: AsyncSession):
        self.retrieval_service = retrieval_service
        self.db = db

    async def compute_fit_score(
        self, resume_id: int, jd_id: int, user_id: int
    ) -> int:
        """计算简历和 JD 的匹配度分数

        算法：
        1. 获取 JD 的内容
        2. 对 JD 的每个关键点，在简历切片中做语义检索
        3. 计算平均相似度
        4. 映射到 0-100 分
        """
        # 获取 JD 文档
        jd_result = await self.db.execute(
            select(Document).where(Document.id == jd_id)
        )
        jd = jd_result.scalar_one_or_none()

        if not jd:
            return 68  # 默认分数

        # 将 JD 内容分割成关键点
        jd_points = self._extract_key_points(jd.content)

        if not jd_points:
            return 68

        # 对每个关键点在简历中检索
        total_similarity = 0
        match_count = 0

        for point in jd_points:
            results = await self.retrieval_service.search_with_scores(
                point, user_id, top_k=3
            )
            if results:
                # 取最高相似度
                max_similarity = max(score for _, score in results)
                total_similarity += max_similarity
                match_count += 1

        if match_count == 0:
            return 68

        # 计算平均相似度并映射到 0-100
        avg_similarity = total_similarity / match_count
        fit_score = int(avg_similarity * 100)

        # 确保在合理范围内
        return max(0, min(100, fit_score))

    def _extract_key_points(self, jd_content: str) -> list[str]:
        """从 JD 内容中提取关键点"""
        # 简单实现：按句子分割
        sentences = jd_content.replace("。", "。\n").replace("；", "；\n").split("\n")
        key_points = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # 过滤太短的句子
                key_points.append(sentence)

        # 限制数量避免过多检索
        return key_points[:10]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd backend && pytest tests/test_matching.py -v`
Expected: `PASSED`

- [ ] **Step 5: 提交更改**

```bash
git add backend/app/services/matching.py backend/tests/test_matching.py
git commit -m "feat: implement MatchingService for fit score calculation"
```

---

## 阶段三：报告增强 + 前端可视化

### Task 3.1: 实现 ECharts 图表组件

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/components/charts/RadarChart.vue`
- Create: `frontend/src/components/charts/TrendChart.vue`

- [ ] **Step 1: 安装 ECharts 依赖**

```bash
cd frontend && npm install echarts vue-echarts
```

- [ ] **Step 2: 创建 RadarChart 组件**

```vue
<!-- frontend/src/components/charts/RadarChart.vue -->
<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: {
    clarity: number
    structure: number
    evidence: number
    reflection: number
  }
}

const props = defineProps<Props>()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chart) return

  const option = {
    radar: {
      indicator: [
        { name: '表达清晰度', max: 100 },
        { name: '结构化程度', max: 100 },
        { name: '证据充分度', max: 100 },
        { name: '复盘深度', max: 100 },
      ],
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              props.data.clarity,
              props.data.structure,
              props.data.evidence,
              props.data.reflection,
            ],
            name: '能力维度',
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.3)',
            },
            lineStyle: {
              color: '#3b82f6',
              width: 2,
            },
            itemStyle: {
              color: '#3b82f6',
            },
          },
        ],
      },
    ],
  }

  chart.setOption(option)
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})
</script>
```

- [ ] **Step 3: 创建 TrendChart 组件**

```vue
<!-- frontend/src/components/charts/TrendChart.vue -->
<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: Array<{
    date: string
    score: number
  }>
}

const props = defineProps<Props>()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chart) return

  const option = {
    xAxis: {
      type: 'category',
      data: props.data.map(item => item.date),
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
    },
    series: [
      {
        data: props.data.map(item => item.score),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.5)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.1)' },
          ]),
        },
        lineStyle: {
          color: '#3b82f6',
          width: 3,
        },
        itemStyle: {
          color: '#3b82f6',
        },
      },
    ],
    tooltip: {
      trigger: 'axis',
    },
  }

  chart.setOption(option)
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})
</script>
```

- [ ] **Step 4: 更新 ReportsPage 集成图表**

```vue
<!-- frontend/src/pages/ReportsPage.vue (部分更新) -->
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">面试报告</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 能力雷达图 -->
      <Card>
        <CardHeader>
          <CardTitle>能力维度分析</CardTitle>
        </CardHeader>
        <CardContent>
          <RadarChart :data="averageScores" />
        </CardContent>
      </Card>

      <!-- 分数趋势图 -->
      <Card>
        <CardHeader>
          <CardTitle>分数趋势</CardTitle>
        </CardHeader>
        <CardContent>
          <TrendChart :data="scoreTrend" />
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import RadarChart from '@/components/charts/RadarChart.vue'
import TrendChart from '@/components/charts/TrendChart.vue'

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
```

- [ ] **Step 5: 提交更改**

```bash
git add frontend/package.json frontend/src/components/charts/ frontend/src/pages/ReportsPage.vue
git commit -m "feat: add ECharts radar and trend charts for reports"
```

---

## 阶段四：工程化补齐

### Task 4.1: 配置结构化日志

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/core/logging.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 添加 structlog 依赖**

```txt
# backend/requirements.txt 添加
structlog==24.4.0
```

- [ ] **Step 2: 创建日志配置**

```python
# backend/app/core/logging.py
import structlog


def setup_logging():
    """配置结构化日志"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            min_level=structlog.stdlib.logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """获取 logger 实例"""
    return structlog.get_logger(name)
```

- [ ] **Step 3: 更新 main.py 添加日志和异常处理**

```python
# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.logging import setup_logging, get_logger
from app.routers import auth, documents, interviews, prep_plans, questions, reports, streams

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="InterviewPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")
app.include_router(prep_plans.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(streams.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
```

- [ ] **Step 4: 验证日志配置**

Run: `cd backend && python -c "from app.core.logging import setup_logging, get_logger; setup_logging(); logger = get_logger('test'); logger.info('test_message', key='value')"`
Expected: JSON 格式的日志输出

- [ ] **Step 5: 提交更改**

```bash
git add backend/requirements.txt backend/app/core/logging.py backend/app/main.py
git commit -m "feat: add structured logging with structlog"
```

---

### Task 4.2: 配置 CI/CD Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: 创建 GitHub Actions 配置**

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  backend:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: pgvector/pgvector:pg17
        env:
          POSTGRES_USER: interviewpilot
          POSTGRES_PASSWORD: interviewpilot
          POSTGRES_DB: interviewpilot
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql+psycopg://interviewpilot:interviewpilot@localhost:5432/interviewpilot
          AI_API_KEY: test-key
        run: |
          cd backend
          pytest -v

      - name: Run linter
        run: |
          cd backend
          pip install ruff
          ruff check .

  frontend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Build
        run: |
          cd frontend
          npm run build

      - name: Run tests
        run: |
          cd frontend
          npm test
```

- [ ] **Step 2: 创建后端 Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: 创建前端 Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 4: 创建 nginx 配置**

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- [ ] **Step 5: 提交更改**

```bash
git add .github/workflows/ci.yml backend/Dockerfile frontend/Dockerfile frontend/nginx.conf
git commit -m "ci: add GitHub Actions CI/CD with Docker support"
```

---

## 自检清单

完成所有任务后，执行以下验证：

### 1. RAG 功能验证
- [ ] 上传一份简历
- [ ] 提问"我在 XX 项目中用了什么技术"
- [ ] 验证回答基于简历内容

### 2. 评分功能验证
- [ ] 提交一段回答
- [ ] 验证返回结构化评分 JSON（四维度分数 + 反馈）

### 3. 匹配度验证
- [ ] 上传简历 + JD
- [ ] 验证 Fit Score 不再是固定值

### 4. 测试验证
```bash
cd backend && pytest -v
```
- [ ] 所有测试通过

### 5. CI 验证
- [ ] Push 到 GitHub 后 Actions 自动运行

### 6. 可视化验证
- [ ] 生成报告后查看雷达图和趋势图

---

## 风险评估和备选方案

### 风险 1: OpenAI API 不可用
**备选方案：** 实现本地 Embedding 模型（如 sentence-transformers）

### 风险 2: pgvector 性能问题
**备选方案：** 使用 Milvus 或 Qdrant 作为向量数据库

### 风险 3: 结构化输出不稳定
**备选方案：** 使用 JSON mode 或 function calling

---

## 时间估算

- 阶段一（RAG）：3-4 天
- 阶段二（AI 评分）：2-3 天
- 阶段三（可视化）：2-3 天
- 阶段四（工程化）：2-3 天
- 阶段五（产品增强）：2-3 天

**总计：11-16 天**

---

## 里程碑

1. **Week 1:** 完成阶段一和阶段二（核心功能）
2. **Week 2:** 完成阶段三和阶段四（工程化）
3. **Week 3:** 完成阶段五（产品增强）并发布

---

## 改进后简历描述

> **InterviewPilot — AI 面试准备平台** | [https://github.com/lanmao657/InterviewPilot-agent](https://github.com/lanmao657/InterviewPilot-agent)
> - 基于 RAG 架构实现简历/JD 语义匹配与智能问答，使用 pgvector + Embedding 构建向量检索 pipeline
> - 设计四维度 AI 评分体系（清晰度/结构化/证据/复盘），通过 LLM 结构化输出实现量化评估
> - 构建文档解析 Pipeline，支持 PDF/DOCX 结构化提取、语义切片与岗位匹配度计算
> - 使用 FastAPI + Vue 3 + PostgreSQL 全栈开发，集成 GitHub Actions CI/CD + Docker 容器化部署
> - 实现 SSE 流式输出、语音输入、ECharts 数据可视化，优化面试模拟体验
