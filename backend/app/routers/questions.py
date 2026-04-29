from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models import PrepPlan, Question, User
from app.schemas import QuestionGenerateRequest, QuestionRead
from app.services.ai_agent import AIAgent

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/generate", response_model=list[QuestionRead])
async def generate_questions(payload: QuestionGenerateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Question]:
    if payload.prep_plan_id:
        plan = db.get(PrepPlan, payload.prep_plan_id)
        if not plan or plan.user_id != user.id:
            raise HTTPException(status_code=404, detail="准备计划不存在")
    generated = await AIAgent().generate_questions(payload.focus, payload.count)
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
