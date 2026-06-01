from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.deps import get_current_user, get_retrieval_service
from app.models import InterviewSession, InterviewStatus, InterviewTurn, PrepPlan, User
from app.schemas import AnswerCreate, InterviewCreate, InterviewRead
from app.services.ai_agent import AIAgent
from app.services.retrieval import RetrievalService

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=InterviewRead)
def create_interview(payload: InterviewCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InterviewSession:
    if payload.prep_plan_id:
        plan = db.get(PrepPlan, payload.prep_plan_id)
        if not plan or plan.user_id != user.id:
            raise HTTPException(status_code=404, detail="准备计划不存在")
    interview = InterviewSession(user_id=user.id, prep_plan_id=payload.prep_plan_id, title=payload.title, status=InterviewStatus.active)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/{interview_id}/answer", response_model=InterviewRead)
async def answer_question(interview_id: int, payload: AnswerCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db), retrieval: RetrievalService = Depends(get_retrieval_service)) -> InterviewSession:
    interview = db.scalar(
        select(InterviewSession).options(selectinload(InterviewSession.turns)).where(InterviewSession.id == interview_id)
    )
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    scored = await AIAgent(retrieval).score_answer(payload.question, payload.answer, user_id=user.id)
    turn = InterviewTurn(
        interview_id=interview.id,
        question=payload.question,
        answer=payload.answer,
        feedback={k: scored[k] for k in ("summary", "strengths", "improvements", "follow_up", "dimensions") if k in scored},
        score=scored["score"],
    )
    db.add(turn)
    db.flush()
    # 重新查询所有轮次的平均分，确保分数准确（替换旧的简单平均算法）
    all_turns = list(db.scalars(select(InterviewTurn).where(InterviewTurn.interview_id == interview.id)).all())
    interview.current_score = round(sum(t.score for t in all_turns) / len(all_turns))
    db.commit()
    return get_interview(interview_id, user, db)


@router.get("/{interview_id}", response_model=InterviewRead)
def get_interview(interview_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InterviewSession:
    interview = db.scalar(
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .where(InterviewSession.id == interview_id, InterviewSession.user_id == user.id)
    )
    if not interview:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    return interview


@router.get("/history/answers")
def get_answer_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    """获取用户所有面试的答案历史，用于跨面试对比"""
    sessions = list(
        db.scalars(
            select(InterviewSession)
            .options(selectinload(InterviewSession.turns))
            .where(InterviewSession.user_id == user.id)
            .order_by(InterviewSession.created_at.desc())
        ).all()
    )
    history: list[dict] = []
    for session in sessions:
        for turn in session.turns:
            history.append({
                "interview_id": session.id,
                "interview_title": session.title,
                "turn_id": turn.id,
                "question": turn.question,
                "answer": turn.answer[:500],
                "score": turn.score,
                "feedback_summary": turn.feedback.get("summary", ""),
                "created_at": turn.created_at.isoformat() if turn.created_at else None,
            })
    return history
