from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user, get_retrieval_service
from app.models import PrepPlan, Question, User
from app.schemas import QuestionGenerateRequest, QuestionRead
from app.services.ai_agent import AIAgent
from app.services.retrieval import RetrievalService

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/generate", response_model=list[QuestionRead])
async def generate_questions(payload: QuestionGenerateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db), retrieval: RetrievalService = Depends(get_retrieval_service)) -> list[Question]:
    if payload.prep_plan_id:
        plan = db.get(PrepPlan, payload.prep_plan_id)
        if not plan or plan.user_id != user.id:
            raise HTTPException(status_code=404, detail="准备计划不存在")
    generated = await AIAgent(retrieval).generate_questions(payload.focus, payload.count, user_id=user.id)
    questions = [
        Question(
            user_id=user.id,
            prep_plan_id=payload.prep_plan_id,
            category=item["category"],
            difficulty=item["difficulty"],
            prompt=item["prompt"],
            rubric=item["rubric"],
        )
        for item in generated
    ]
    db.add_all(questions)
    db.commit()
    for question in questions:
        db.refresh(question)
    return questions


@router.get("", response_model=list[QuestionRead])
def list_questions(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Question]:
    return list(db.scalars(select(Question).where(Question.user_id == user.id).order_by(Question.created_at.desc())).all())


@router.post("/answer-cards")
async def generate_answer_cards(user: User = Depends(get_current_user), db: Session = Depends(get_db), retrieval: RetrievalService = Depends(get_retrieval_service)) -> list[dict]:
    """为用户题库中的题目生成 STAR 话术卡片"""
    questions = list(db.scalars(select(Question).where(Question.user_id == user.id).order_by(Question.created_at.desc()).limit(6)).all())
    if not questions:
        raise HTTPException(status_code=400, detail="题库为空，请先生成题目")
    q_dicts = [{"prompt": q.prompt, "category": q.category, "difficulty": q.difficulty} for q in questions]
    return await AIAgent(retrieval).generate_answer_cards(q_dicts, user_id=user.id)
