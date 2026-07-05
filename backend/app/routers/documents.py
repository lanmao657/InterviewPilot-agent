import asyncio
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.deps import get_current_user, get_retrieval_service
from app.models import Document, DocumentKind, User
from app.schemas import DocumentRead
from app.services.ai_agent import AIAgent
from app.services.documents import DocumentService, extract_upload_text, summarize_document
from app.services.embedding import EmbeddingService
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


class JDTextInput(BaseModel):
    """JD 纯文本输入"""
    text: str = Field(min_length=10, max_length=50000)
    filename: str = "pasted-jd.txt"


async def _process_embedding(document_id: int) -> None:
    """后台任务：独立 session 完成切片+向量化"""
    db = SessionLocal()
    try:
        embedding_service = EmbeddingService()
        document_service = DocumentService(embedding_service, db)
        await document_service.process_document(document_id)
    except Exception as e:
        logger.error(f"文档切片处理失败: {e}")
    finally:
        db.close()


async def _save_document(kind: DocumentKind, file: UploadFile, user: User, db: Session) -> Document:
    text = await extract_upload_text(file)
    doc = Document(
        user_id=user.id,
        kind=kind,
        filename=file.filename or "uploaded-file",
        content=text,
        summary=summarize_document(text, kind.value),
        embedding_status="pending",
        embedding_error=None,
        chunk_count=0,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 后台异步处理切片和向量化，不阻塞响应
    asyncio.create_task(_process_embedding(doc.id))

    return doc


@router.post("/resume", response_model=DocumentRead)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Document:
    return await _save_document(DocumentKind.resume, file, user, db)


@router.post("/job-description", response_model=DocumentRead)
async def upload_jd(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Document:
    return await _save_document(DocumentKind.job_description, file, user, db)


@router.post("/job-description-text", response_model=DocumentRead)
async def upload_jd_text(payload: JDTextInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Document:
    """通过纯文本上传 JD（支持直接粘贴）"""
    text = payload.text.strip()
    doc = Document(
        user_id=user.id,
        kind=DocumentKind.job_description,
        filename=payload.filename,
        content=text,
        summary=summarize_document(text, "job_description"),
        embedding_status="pending",
        embedding_error=None,
        chunk_count=0,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 后台异步处理切片和向量化，不阻塞响应
    asyncio.create_task(_process_embedding(doc.id))

    return doc


@router.get("", response_model=list[DocumentRead])
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())).all())


@router.post("/{document_id}/analyze", response_model=DocumentRead)
async def analyze_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> Document:
    """对文档进行 AI 诊断评分（仅限简历类型），支持重复诊断"""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="文档不存在")
    if doc.kind != DocumentKind.resume:
        raise HTTPException(status_code=400, detail="仅支持简历文档的诊断")

    # 每次都重新诊断，不使用缓存
    analysis = await AIAgent(retrieval).analyze_resume(doc.content, user_id=user.id)
    doc.analysis = analysis
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/{document_id}/rewrite")
async def rewrite_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> dict:
    """简历优化重写：根据 JD 给出具体的改写建议"""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="文档不存在")
    if doc.kind != DocumentKind.resume:
        raise HTTPException(status_code=400, detail="仅支持简历文档的优化")

    # 获取用户最新的 JD
    jd = db.scalar(
        select(Document)
        .where(Document.user_id == user.id, Document.kind == DocumentKind.job_description)
        .order_by(Document.created_at.desc())
        .limit(1)
    )
    jd_text = jd.content if jd else ""

    agent = AIAgent(retrieval)
    return await agent.rewrite_resume(doc.content, jd_text, user_id=user.id)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    """删除文档及其关联的切片（级联删除由 ORM cascade 处理）"""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="文档不存在")
    db.delete(doc)
    db.commit()
