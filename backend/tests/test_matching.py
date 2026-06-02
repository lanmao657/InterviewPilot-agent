import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.matching import MatchingService


@pytest.fixture
def mock_retrieval_service():
    """模拟检索服务，包含 embedding_service"""
    service = AsyncMock()
    # 模拟批量 embedding 返回（每个关键点一个向量）
    service.embedding_service.embed = AsyncMock(return_value=[
        [0.1] * 1024,
        [0.2] * 1024,
        [0.3] * 1024,
    ])
    return service


@pytest.fixture
def mock_db():
    db = MagicMock()
    # 模拟 pgvector 检索结果：返回 (chunk, distance) 行
    mock_chunk = MagicMock()
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, key: mock_chunk if key == 0 else 0.15
    mock_row._mapping = {0: mock_chunk, 'distance': 0.15}
    db.execute.return_value.all.return_value = [(mock_chunk, 0.15)]
    return db


@pytest.fixture
def matching_service(mock_retrieval_service, mock_db):
    return MatchingService(mock_retrieval_service, mock_db)


@pytest.mark.asyncio
async def test_compute_fit_score(matching_service, mock_retrieval_service):
    """测试计算匹配度分数"""
    # 模拟 JD 文档
    mock_jd = MagicMock()
    mock_jd.content = "岗位要求：Python, FastAPI, PostgreSQL"

    # 模拟 pgvector 检索结果：cosine_distance = 0.15 → similarity = 0.85
    mock_chunk = MagicMock()
    mock_pgvector_result = MagicMock()
    mock_pgvector_result.all.return_value = [(mock_chunk, 0.15)]

    # 模拟数据库查询：第一次返回 JD 文档，第二次返回 pgvector 结果
    mock_jd_result = MagicMock()
    mock_jd_result.scalar_one_or_none.return_value = mock_jd
    matching_service.db.execute.side_effect = [mock_jd_result, mock_pgvector_result]

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
