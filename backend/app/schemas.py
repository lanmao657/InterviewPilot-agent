from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import DocumentKind, InterviewStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = "候选人"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str


class DocumentRead(BaseModel):
    id: int
    kind: DocumentKind
    filename: str
    summary: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class PrepPlanCreate(BaseModel):
    resume_id: int | None = None
    job_description_id: int | None = None
    title: str = "AI 面试准备计划"
    target_role: str = "目标岗位"


class PrepPlanRead(BaseModel):
    id: int
    title: str
    target_role: str
    fit_score: int
    status: str
    roadmap: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionGenerateRequest(BaseModel):
    prep_plan_id: int | None = None
    count: int = Field(default=6, ge=1, le=12)
    focus: str = "综合能力"


class QuestionRead(BaseModel):
    id: int
    prep_plan_id: int | None
    category: str
    difficulty: str
    prompt: str
    rubric: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewCreate(BaseModel):
    prep_plan_id: int | None = None
    title: str = "模拟面试"


class AnswerCreate(BaseModel):
    question: str
    answer: str


class TurnRead(BaseModel):
    id: int
    question: str
    answer: str
    feedback: dict
    score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewRead(BaseModel):
    id: int
    prep_plan_id: int | None
    title: str
    status: InterviewStatus
    current_score: int
    turns: list[TurnRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportRead(BaseModel):
    id: int
    interview_id: int
    title: str
    overall_score: int
    content: str
    metrics: dict
    created_at: datetime

    model_config = {"from_attributes": True}
