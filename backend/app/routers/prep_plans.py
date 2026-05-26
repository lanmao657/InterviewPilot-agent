from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models import Document, PrepPlan, User
from app.schemas import PrepPlanCreate, PrepPlanRead
from app.services.ai_agent import AIAgent

router = APIRouter(prefix="/prep-plans", tags=["prep-plans"])


@router.post("", response_model=PrepPlanRead)
async def create_plan(payload: PrepPlanCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PrepPlan:
    resume = db.get(Document, payload.resume_id) if payload.resume_id else None
    jd = db.get(Document, payload.job_description_id) if payload.job_description_id else None
    if resume and resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="简历不存在")
    if jd and jd.user_id != user.id:
        raise HTTPException(status_code=404, detail="JD 不存在")

    roadmap = await AIAgent().build_roadmap(resume.content if resume else "", jd.content if jd else "", payload.target_role, user_id=user.id)
    plan = PrepPlan(
        user_id=user.id,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        title=payload.title,
        target_role=payload.target_role,
        fit_score=78 if resume and jd else 68,
        roadmap=roadmap,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=list[PrepPlanRead])
def list_plans(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PrepPlan]:
    return list(db.scalars(select(PrepPlan).where(PrepPlan.user_id == user.id).order_by(PrepPlan.created_at.desc())).all())


@router.get("/{plan_id}", response_model=PrepPlanRead)
def get_plan(plan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PrepPlan:
    plan = db.get(PrepPlan, plan_id)
    if not plan or plan.user_id != user.id:
        raise HTTPException(status_code=404, detail="准备计划不存在")
    return plan
