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
