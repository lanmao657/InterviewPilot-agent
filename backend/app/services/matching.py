from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Document
from app.services.retrieval import RetrievalService


class MatchingService:
    def __init__(self, retrieval_service: RetrievalService, db: Session):
        self.retrieval_service = retrieval_service
        self.db = db

    async def compute_fit_score(
        self, resume_id: int, jd_id: int, user_id: int
    ) -> int:
        """计算简历和 JD 的匹配度分数

        算法：
        1. 获取 JD 的内容
        2. 对 JD 的每个关键点，在简历切片中做语义检索
        3. 计算平均相似度
        4. 映射到 0-100 分
        """
        # 获取 JD 文档
        jd_result = self.db.execute(
            select(Document).where(Document.id == jd_id)
        )
        jd = jd_result.scalar_one_or_none()

        if not jd:
            return 68  # 默认分数

        # 将 JD 内容分割成关键点
        jd_points = self._extract_key_points(jd.content)

        if not jd_points:
            return 68

        # 批量对所有关键点做 embedding（一次 API 调用替代 N 次）
        # 然后逐个做 pgvector 检索
        embeddings = await self.retrieval_service.embedding_service.embed(jd_points)

        total_similarity = 0
        match_count = 0

        for i, point in enumerate(jd_points):
            # 使用预计算的 embedding 直接检索
            query_vector = embeddings[i] if i < len(embeddings) else None
            if query_vector is None:
                continue

            from app.models.document_chunk import DocumentChunk
            stmt = (
                select(
                    DocumentChunk,
                    DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
                )
                .where(DocumentChunk.user_id == user_id, DocumentChunk.document_id == resume_id)
                .order_by("distance")
                .limit(3)
            )
            rows = self.db.execute(stmt).all()
            if rows:
                max_similarity = max(1 - distance for _, distance in rows)
                total_similarity += max_similarity
                match_count += 1

        if match_count == 0:
            return 68

        # 计算平均相似度并映射到 0-100
        avg_similarity = total_similarity / match_count
        fit_score = int(avg_similarity * 100)

        # 确保在合理范围内
        return max(0, min(100, fit_score))

    def _extract_key_points(self, jd_content: str) -> list[str]:
        """从 JD 内容中提取关键点"""
        # 简单实现：按句子分割
        sentences = jd_content.replace("。", "。\n").replace("；", "；\n").split("\n")
        key_points = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # 过滤太短的句子
                key_points.append(sentence)

        # 限制数量避免过多检索
        return key_points[:10]
