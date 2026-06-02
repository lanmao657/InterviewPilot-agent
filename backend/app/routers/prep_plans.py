import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.deps import get_current_user, get_retrieval_service
from app.models import Document, PrepPlan, User
from app.schemas import PrepPlanCreate, PrepPlanRead
from app.services.ai_agent import AIAgent
from app.services.matching import MatchingService
from app.services.retrieval import RetrievalService

router = APIRouter(prefix="/prep-plans", tags=["prep-plans"])
logger = get_logger(__name__)


@router.post("/jd-match")
async def analyze_jd_match(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> dict:
    """JD 匹配差距分析：对比用户最新简历和 JD"""
    from app.models import DocumentKind
    resume = db.scalar(select(Document).where(Document.user_id == user.id, Document.kind == DocumentKind.resume).order_by(Document.created_at.desc()).limit(1))
    jd = db.scalar(select(Document).where(Document.user_id == user.id, Document.kind == DocumentKind.job_description).order_by(Document.created_at.desc()).limit(1))
    if not resume or not jd:
        raise HTTPException(status_code=400, detail="请先上传简历和 JD")
    agent = AIAgent(retrieval)
    return await agent.analyze_jd_match(resume.content, jd.content, user_id=user.id)


@router.post("", response_model=PrepPlanRead)
async def create_plan(payload: PrepPlanCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db), retrieval: RetrievalService = Depends(get_retrieval_service)) -> PrepPlan:
    resume = db.get(Document, payload.resume_id) if payload.resume_id else None
    jd = db.get(Document, payload.job_description_id) if payload.job_description_id else None
    if resume and resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="简历不存在")
    if jd and jd.user_id != user.id:
        raise HTTPException(status_code=404, detail="JD 不存在")

    agent = AIAgent(retrieval)
    resume_text = resume.content if resume else ""
    jd_text = jd.content if jd else ""

    # 并行执行 build_roadmap 和 extract_jd_keywords，节省约 3-5 秒
    async def _build_roadmap():
        try:
            return await agent.build_roadmap(resume_text, jd_text, payload.target_role, user_id=user.id)
        except Exception as exc:
            logger.error("build_roadmap_failed", error=str(exc), exc_info=True)
            return {
                "summary": "AI 分析暂时不可用，请稍后重试",
                "milestones": ["岗位匹配分析", "高频题训练", "STAR 表达打磨", "模拟面试复盘"],
                "focusAreas": ["业务理解", "项目深挖", "结构化表达", "反问准备"],
                "strengths": [],
                "gaps": [],
            }

    async def _extract_keywords():
        if not jd:
            return []
        try:
            data = await agent.extract_jd_keywords(jd_text, user_id=user.id)
            return data.get("keywords", [])
        except Exception as exc:
            logger.error("extract_jd_keywords_failed", error=str(exc), exc_info=True)
            return []

    roadmap, keywords = await asyncio.gather(_build_roadmap(), _extract_keywords())
    roadmap["keywords"] = keywords

    if resume and jd:
        try:
            fit_score = await MatchingService(retrieval, db).compute_fit_score(resume.id, jd.id, user.id)
        except Exception:
            fit_score = 68
    else:
        fit_score = 68

    plan = PrepPlan(
        user_id=user.id,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        title=payload.title,
        target_role=payload.target_role,
        fit_score=fit_score,
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
