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
    db = MagicMock()
    db.execute = AsyncMock()
    db.execute.return_value = MagicMock()
    return db


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


@pytest.mark.asyncio
async def test_search_returns_empty_on_no_embedding(retrieval_service, mock_embedding_service):
    """测试当 embedding 返回空时，检索返回空列表"""
    mock_embedding_service.embed.return_value = []

    results = await retrieval_service.search("测试查询", user_id=1, top_k=3)

    assert results == []
    mock_embedding_service.embed.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_scores_returns_tuples(retrieval_service, mock_embedding_service):
    """测试带分数的检索返回 (content, score) 元组"""
    mock_chunk = MagicMock()
    mock_chunk.content = "测试内容"

    # 模拟返回 (chunk, distance) 元组
    mock_row = (mock_chunk, 0.2)
    retrieval_service.db.execute.return_value.all.return_value = [mock_row]

    results = await retrieval_service.search_with_scores("测试查询", user_id=1, top_k=3)

    assert len(results) > 0
    content, score = results[0]
    assert content == "测试内容"
    assert score == pytest.approx(0.8)  # 1 - 0.2 = 0.8
    mock_embedding_service.embed.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_scores_returns_empty_on_no_embedding(
    retrieval_service, mock_embedding_service
):
    """测试当 embedding 返回空时，带分数的检索返回空列表"""
    mock_embedding_service.embed.return_value = []

    results = await retrieval_service.search_with_scores("测试查询", user_id=1, top_k=3)

    assert results == []
    mock_embedding_service.embed.assert_called_once()


@pytest.mark.asyncio
async def test_search_respects_top_k(retrieval_service, mock_embedding_service):
    """测试检索遵守 top_k 参数"""
    mock_chunks = []
    for i in range(5):
        mock_chunk = MagicMock()
        mock_chunk.content = f"内容{i}"
        mock_chunks.append(mock_chunk)

    retrieval_service.db.execute.return_value.scalars.return_value.all.return_value = (
        mock_chunks[:3]
    )

    results = await retrieval_service.search("测试查询", user_id=1, top_k=3)

    assert len(results) == 3
