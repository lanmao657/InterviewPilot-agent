import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.deps import get_current_user, get_retrieval_service
from app.models import InterviewSession, Report, User
from app.schemas import ReportRead
from app.services.ai_agent import AIAgent
from app.services.retrieval import RetrievalService

router = APIRouter(prefix="/reports", tags=["reports"])


def _format_report_content(report_data: str | dict) -> str:
    """将报告数据转为人类可读的文本"""
    if isinstance(report_data, str):
        return report_data
    if not isinstance(report_data, dict):
        return str(report_data)

    parts: list[str] = []
    if overall := report_data.get("overall"):
        parts.append(f"【整体评价】\n{overall}")
    if avg := report_data.get("average_scores"):
        dim_labels = {"clarity": "表达清晰度", "structure": "结构化程度", "evidence": "证据充分度", "reflection": "复盘深度"}
        lines = [f"  {dim_labels.get(k, k)}: {v} 分" for k, v in avg.items()]
        parts.append("【各维度评分】\n" + "\n".join(lines))
    if improvements := report_data.get("improvements"):
        items = "\n".join(f"  - {item}" for item in improvements)
        parts.append(f"【改进建议】\n{items}")
    if next_steps := report_data.get("next_steps"):
        items = "\n".join(f"  - {item}" for item in next_steps)
        parts.append(f"【下一步行动计划】\n{items}")
    return "\n\n".join(parts) if parts else json.dumps(report_data, ensure_ascii=False)


def _extract_metrics(report_data: str | dict, scores: list[int]) -> dict:
    """从报告数据中提取各维度分数，用于雷达图展示（英文 key）"""
    if isinstance(report_data, dict) and "average_scores" in report_data:
        avg = report_data["average_scores"]
        return {
            "clarity": int(avg.get("clarity", 0)),
            "structure": int(avg.get("structure", 0)),
            "evidence": int(avg.get("evidence", 0)),
            "reflection": int(avg.get("reflection", 0)),
        }
    base = round(sum(scores) / len(scores)) if scores else 0
    return {"clarity": base, "structure": base, "evidence": base, "reflection": base}


@router.post("/{interview_id}", response_model=ReportRead)
async def create_report(interview_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db), retrieval: RetrievalService = Depends(get_retrieval_service)) -> Report:
    interview = db.scalar(
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .where(InterviewSession.id == interview_id, InterviewSession.user_id == user.id)
    )
    if not interview:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    existing = db.scalar(select(Report).where(Report.interview_id == interview_id, Report.user_id == user.id))
    if existing:
        return existing

    turns = [{"question": turn.question, "answer": turn.answer, "score": turn.score} for turn in interview.turns]
    report_data = await AIAgent(retrieval).build_report(interview.title, turns, user_id=user.id)
    content = _format_report_content(report_data)
    scores = [turn.score for turn in interview.turns]

    metrics = _extract_metrics(report_data, scores)

    report = Report(
        user_id=user.id,
        interview_id=interview.id,
        title=f"{interview.title}复盘报告",
        overall_score=round(sum(scores) / len(scores)) if scores else 0,
        content=content,
        metrics=metrics,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[ReportRead])
def list_reports(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Report]:
    return list(db.scalars(select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc())).all())


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Report:
    report = db.get(Report, report_id)
    if not report or report.user_id != user.id:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report
