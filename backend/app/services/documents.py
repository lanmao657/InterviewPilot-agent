from io import BytesIO

from docx import Document as DocxDocument
from fastapi import UploadFile
from pypdf import PdfReader


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
