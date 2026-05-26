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
