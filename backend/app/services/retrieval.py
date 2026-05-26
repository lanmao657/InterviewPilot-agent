from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding import EmbeddingService


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService, db: Session):
        self.embedding_service = embedding_service
        self.db = db

    async def search(
        self, query: str, user_id: int, top_k: int = 5
    ) -> list[str]:
        """1. 对 query 做 embedding
           2. 在 document_chunks 中做 L2 distance 检索
           3. 返回 top_k 相关片段
        """
        # 1. 对查询文本做 embedding
        query_embedding = await self.embedding_service.embed([query])
        if not query_embedding:
            return []

        query_vector = query_embedding[0]

        # 2. 使用 pgvector 的 L2 distance 检索
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.embedding.l2_distance(query_vector))
            .limit(top_k)
        )

        result = self.db.execute(stmt)
        chunks = result.scalars().all()

        # 3. 返回相关片段内容
        return [chunk.content for chunk in chunks]

    async def search_with_scores(
        self, query: str, user_id: int, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """返回相关片段及其相似度分数"""
        query_embedding = await self.embedding_service.embed([query])
        if not query_embedding:
            return []

        query_vector = query_embedding[0]

        # 使用 cosine distance
        stmt = (
            select(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
            )
            .where(DocumentChunk.user_id == user_id)
            .order_by("distance")
            .limit(top_k)
        )

        result = self.db.execute(stmt)
        rows = result.all()

        # cosine_distance = 1 - cosine_similarity, 返回范围 [-1, 1]
        return [(chunk.content, 1 - distance) for chunk, distance in rows]
