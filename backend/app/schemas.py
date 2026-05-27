from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import DocumentKind, InterviewStatus


PASSWORD_RULES = "密码至少需要 8 个字符"


def normalize_username(value: str) -> str:
    username = value.strip().casefold()
    if not username:
        raise ValueError("用户名不能为空")
    if len(username) < 3:
        raise ValueError("用户名至少需要 3 个字符")
    if len(username) > 120:
        raise ValueError("用户名最多 120 个字符")
    if "@" in username:
        raise ValueError("用户名不能使用邮箱格式")
    return username


def normalize_login_identifier(value: str) -> str:
    identifier = value.strip().casefold()
    if not identifier:
        raise ValueError("用户名或邮箱不能为空")
    if "@" in identifier:
        return identifier
    return normalize_username(identifier)


def validate_password(value: str) -> str:
    if not value:
        raise ValueError("密码不能为空")
    if len(value) < 8:
        raise ValueError(PASSWORD_RULES)
    return value


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return normalize_login_identifier(value)


class UserRead(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr | None = None
    is_anonymous: bool = False

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


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: int | None = None


class AssistantContextRead(BaseModel):
    documents: list[dict]
    activePlan: dict | None = None
    questionCount: int
    recentInterview: dict | None = None
    latestReport: dict | None = None


class AssistantChatResponse(BaseModel):
    answer: str
    context: AssistantContextRead
    conversation: "AssistantConversationRead"
    messages: list["AssistantMessageRead"]


class AssistantMessageRead(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    status: str
    metadata: dict = Field(validation_alias="meta", serialization_alias="metadata")
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class AssistantConversationRead(BaseModel):
    id: int
    title: str
    scope: str
    metadata: dict = Field(validation_alias="meta", serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    messages: list[AssistantMessageRead] = []

    model_config = {"from_attributes": True, "populate_by_name": True}
