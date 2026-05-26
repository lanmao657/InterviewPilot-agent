import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.deps import get_current_user
from app.models import InterviewSession, Report, User
from app.schemas import ReportRead
from app.services.ai_agent import AIAgent

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{interview_id}", response_model=ReportRead)
async def create_report(interview_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Report:
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
    report_data = await AIAgent().build_report(interview.title, turns, user_id=user.id)
    content = report_data if isinstance(report_data, str) else json.dumps(report_data, ensure_ascii=False)
    scores = [turn.score for turn in interview.turns]
    report = Report(
        user_id=user.id,
        interview_id=interview.id,
        title=f"{interview.title}复盘报告",
        overall_score=round(sum(scores) / len(scores)) if scores else 0,
        content=content,
        metrics={"表达结构": 78, "岗位匹配": 82, "证据质量": 74, "复盘深度": 76},
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
