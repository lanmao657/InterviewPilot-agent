import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.models import DocumentChunk
from app.services.documents import DocumentService


@pytest.fixture
def mock_embedding_service():
    service = AsyncMock()
    service.embed.return_value = [[0.1] * 1536, [0.2] * 1536]
    # chunk_text is a synchronous method, use MagicMock for it
    service.chunk_text = MagicMock(return_value=["chunk1", "chunk2"])
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

    # 模拟数据库查询返回文档
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_document
    mock_db.execute.return_value = mock_result

    await document_service.process_document(1)

    assert mock_document.embedding_status == "ready"
    assert mock_document.embedding_error is None
    assert mock_document.chunk_count == 2

    # 验证调用了切片
    mock_embedding_service.chunk_text.assert_called_once_with("测试文档内容")

    # 验证调用了 embedding
    mock_embedding_service.embed.assert_called_once_with(["chunk1", "chunk2"])

    # 验证数据库添加了 2 个切片记录
    added_chunks = [
        call.args[0]
        for call in mock_db.add.call_args_list
        if isinstance(call.args[0], DocumentChunk)
    ]
    assert len(added_chunks) == 2

    # 验证提交了 processing 和 ready 两个状态
    assert mock_db.commit.call_count == 2


@pytest.mark.asyncio
async def test_process_document_nonexistent_document(
    document_service, mock_embedding_service, mock_db
):
    """测试处理不存在的文档时不做任何操作"""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    await document_service.process_document(999)

    # 验证未调用切片和 embedding
    mock_embedding_service.chunk_text.assert_not_called()
    mock_embedding_service.embed.assert_not_called()
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_summarize_document_resume(document_service):
    """测试简历摘要生成"""
    result = document_service.summarize_document("测试简历内容", "resume")

    assert result["type"] == "简历"
    assert "项目经历" in result["highlights"]
    assert "核心技能" in result["highlights"]
    assert result["preview"] == "测试简历内容"


def test_summarize_document_jd(document_service):
    """测试 JD 摘要生成"""
    result = document_service.summarize_document("测试 JD 内容", "job_description")

    assert result["type"] == "JD"
    assert "岗位职责" in result["highlights"]
    assert result["preview"] == "测试 JD 内容"


@pytest.mark.asyncio
async def test_process_document_records_embedding_failure(
    document_service, mock_embedding_service, mock_db
):
    """测试向量化失败会记录到文档状态"""
    mock_document = MagicMock()
    mock_document.id = 1
    mock_document.user_id = 1
    mock_document.content = "测试文档内容"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_document
    mock_db.execute.return_value = mock_result
    mock_embedding_service.embed.side_effect = RuntimeError("provider down")

    await document_service.process_document(1)

    assert mock_document.embedding_status == "failed"
    assert mock_document.chunk_count == 0
    assert mock_document.embedding_error == "文档语义索引建立失败，请稍后重试。"
    mock_db.rollback.assert_called_once()
    assert mock_db.commit.call_count == 2


@pytest.mark.asyncio
async def test_process_document_marks_empty_text_as_failed(
    document_service, mock_embedding_service, mock_db
):
    """测试空文本不会被标记为可检索"""
    mock_document = MagicMock()
    mock_document.id = 1
    mock_document.user_id = 1
    mock_document.content = "   "

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_document
    mock_db.execute.return_value = mock_result
    mock_embedding_service.chunk_text.return_value = []

    await document_service.process_document(1)

    assert mock_document.embedding_status == "failed"
    assert mock_document.chunk_count == 0
    assert mock_document.embedding_error == "未解析到可用于索引的文本，请检查文件内容。"
    mock_embedding_service.embed.assert_not_called()
