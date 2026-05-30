import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user, get_retrieval_service
from app.models import Document, DocumentKind, User
from app.schemas import DocumentRead
from app.services.ai_agent import AIAgent
from app.services.documents import DocumentService, extract_upload_text, summarize_document
from app.services.embedding import EmbeddingService
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


async def _save_document(kind: DocumentKind, file: UploadFile, user: User, db: Session) -> Document:
    text = await extract_upload_text(file)
    doc = Document(
        user_id=user.id,
        kind=kind,
        filename=file.filename or "uploaded-file",
        content=text,
        summary=summarize_document(text, kind.value),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 异步处理切片和向量化（失败不影响文档上传）
    try:
        embedding_service = EmbeddingService()
        document_service = DocumentService(embedding_service, db)
        await document_service.process_document(doc.id)
    except Exception as e:
        logger.error(f"文档切片处理失败: {e}")

    return doc


@router.post("/resume", response_model=DocumentRead)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Document:
    return await _save_document(DocumentKind.resume, file, user, db)


@router.post("/job-description", response_model=DocumentRead)
async def upload_jd(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Document:
    return await _save_document(DocumentKind.job_description, file, user, db)


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
    """对文档进行 AI 诊断评分（仅限简历类型）"""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="文档不存在")
    if doc.kind != DocumentKind.resume:
        raise HTTPException(status_code=400, detail="仅支持简历文档的诊断")

    # 如果已有诊断结果，直接返回
    if doc.analysis:
        return doc

    analysis = await AIAgent(retrieval).analyze_resume(doc.content, user_id=user.id)
    doc.analysis = analysis
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    """删除文档及其关联的切片（级联删除由 ORM cascade 处理）"""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="文档不存在")
    db.delete(doc)
    db.commit()
