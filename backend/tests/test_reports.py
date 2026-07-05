from app.routers.reports import _format_report_content
from app.services.ai_agent import AI_NOTICE_KEY


def test_format_report_content_includes_ai_fallback_notice() -> None:
    content = _format_report_content(
        {
            AI_NOTICE_KEY: "AI 服务暂时不可用，已使用本地示例结果。",
            "overall": "整体表现良好。",
            "average_scores": {"clarity": 70},
        }
    )

    assert content.startswith("【AI 提示】\nAI 服务暂时不可用，已使用本地示例结果。")
