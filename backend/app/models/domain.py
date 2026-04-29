from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DocumentKind(str, Enum):
    resume = "resume"
    job_description = "job_description"


class InterviewStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="候选人")
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    documents: Mapped[list["Document"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    prep_plans: Mapped[list["PrepPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    interviews: Mapped[list["InterviewSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[DocumentKind] = mapped_column(SAEnum(DocumentKind))
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="documents")


class PrepPlan(Base):
    __tablename__ = "prep_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    job_description_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(180))
    target_role: Mapped[str] = mapped_column(String(180), default="目标岗位")
    fit_score: Mapped[int] = mapped_column(Integer, default=72)
    status: Mapped[str] = mapped_column(String(40), default="active")
    roadmap: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="prep_plans")
    questions: Mapped[list["Question"]] = relationship(back_populates="prep_plan", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    prep_plan_id: Mapped[int | None] = mapped_column(ForeignKey("prep_plans.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(80))
    difficulty: Mapped[str] = mapped_column(String(40), default="medium")
    prompt: Mapped[str] = mapped_column(Text)
    rubric: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prep_plan: Mapped[PrepPlan | None] = relationship(back_populates="questions")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    prep_plan_id: Mapped[int | None] = mapped_column(ForeignKey("prep_plans.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(180))
    status: Mapped[InterviewStatus] = mapped_column(SAEnum(InterviewStatus), default=InterviewStatus.active)
    current_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="interviews")
    turns: Mapped[list["InterviewTurn"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    report: Mapped["Report | None"] = relationship(back_populates="interview", cascade="all, delete-orphan")


class InterviewTurn(Base):
    __tablename__ = "interview_turns"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, default="")
    feedback: Mapped[dict] = mapped_column(JSON, default=dict)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    interview: Mapped[InterviewSession] = relationship(back_populates="turns")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"), unique=True)
    title: Mapped[str] = mapped_column(String(180))
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    interview: Mapped[InterviewSession] = relationship(back_populates="report")
