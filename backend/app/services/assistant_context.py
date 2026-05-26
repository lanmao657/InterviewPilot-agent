from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Document, InterviewSession, PrepPlan, Question, Report, User


def build_assistant_context(db: Session, user: User) -> dict:
    documents = list(
        db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc()).limit(4)).all()
    )
    active_plan = db.scalar(select(PrepPlan).where(PrepPlan.user_id == user.id).order_by(PrepPlan.created_at.desc()).limit(1))
    question_count = db.scalar(select(func.count(Question.id)).where(Question.user_id == user.id)) or 0
    recent_interview = db.scalar(
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .where(InterviewSession.user_id == user.id)
        .order_by(InterviewSession.created_at.desc())
        .limit(1)
    )
    latest_report = db.scalar(select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc()).limit(1))

    return {
        "documents": [
            {
                "id": document.id,
                "kind": document.kind.value,
                "filename": document.filename,
                "summary": document.summary,
                "contentPreview": document.content[:1200],
            }
            for document in documents
        ],
        "activePlan": (
            {
                "id": active_plan.id,
                "title": active_plan.title,
                "targetRole": active_plan.target_role,
                "fitScore": active_plan.fit_score,
                "roadmap": active_plan.roadmap,
            }
            if active_plan
            else None
        ),
        "questionCount": question_count,
        "recentInterview": (
            {
                "id": recent_interview.id,
                "title": recent_interview.title,
                "currentScore": recent_interview.current_score,
                "turnCount": len(recent_interview.turns),
                "latestTurn": (
                    {
                        "question": recent_interview.turns[-1].question,
                        "answer": recent_interview.turns[-1].answer[:1200],
                        "score": recent_interview.turns[-1].score,
                        "feedback": recent_interview.turns[-1].feedback,
                    }
                    if recent_interview.turns
                    else None
                ),
            }
            if recent_interview
            else None
        ),
        "latestReport": (
            {
                "id": latest_report.id,
                "title": latest_report.title,
                "overallScore": latest_report.overall_score,
                "contentPreview": latest_report.content[:1200],
                "metrics": latest_report.metrics,
            }
            if latest_report
            else None
        ),
    }
