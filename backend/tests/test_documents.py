import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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

    # 验证调用了切片
    mock_embedding_service.chunk_text.assert_called_once_with("测试文档内容")

    # 验证调用了 embedding
    mock_embedding_service.embed.assert_called_once_with(["chunk1", "chunk2"])

    # 验证数据库添加了 2 个切片记录
    assert mock_db.add.call_count == 2

    # 验证提交了数据库
    mock_db.commit.assert_called_once()


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
