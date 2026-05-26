from io import BytesIO

from docx import Document as DocxDocument
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services.embedding import EmbeddingService


async def extract_upload_text(file: UploadFile) -> str:
    data = await file.read()
    filename = file.filename or "uploaded-file"
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if suffix == "pdf":
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix == "docx":
        doc = DocxDocument(BytesIO(data))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    return data.decode("utf-8", errors="ignore").strip()


def summarize_document(text: str, kind: str) -> dict:
    """生成文档摘要（保留向后兼容）"""
    compact = " ".join(text.split())[:600]
    if kind == "resume":
        return {
            "type": "简历",
            "highlights": ["项目经历", "核心技能", "过往职责"],
            "preview": compact or "未解析到文本，请检查文件内容。",
        }
    return {
        "type": "JD",
        "highlights": ["岗位职责", "能力要求", "面试关注点"],
        "preview": compact or "未解析到文本，请检查文件内容。",
    }


class DocumentService:
    def __init__(self, embedding_service: EmbeddingService, db: Session):
        self.embedding_service = embedding_service
        self.db = db

    async def process_document(self, document_id: int) -> None:
        """处理文档：切片 + 向量化"""
        # 获取文档
        result = self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            return

        # 切片
        chunks = self.embedding_service.chunk_text(document.content)

        # 生成 embeddings
        embeddings = await self.embedding_service.embed(chunks)

        # 保存切片到数据库
        for i, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=document_id,
                user_id=document.user_id,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding,
            )
            self.db.add(chunk)

        self.db.commit()

    def summarize_document(self, text: str, kind: str) -> dict:
        """生成文档摘要"""
        return summarize_document(text, kind)
