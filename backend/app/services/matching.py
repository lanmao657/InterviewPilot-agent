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

        # 对每个关键点在简历中检索
        total_similarity = 0
        match_count = 0

        for point in jd_points:
            results = await self.retrieval_service.search_with_scores(
                point, user_id, top_k=3, document_id=resume_id
            )
            if results:
                # 取最高相似度
                max_similarity = max(score for _, score in results)
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
