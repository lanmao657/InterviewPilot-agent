from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models import Document, DocumentKind, User
from app.schemas import DocumentRead
from app.services.documents import DocumentService, extract_upload_text, summarize_document
from app.services.embedding import EmbeddingService

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

    # 异步处理切片和向量化
    embedding_service = EmbeddingService()
    document_service = DocumentService(embedding_service, db)
    await document_service.process_document(doc.id)

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
