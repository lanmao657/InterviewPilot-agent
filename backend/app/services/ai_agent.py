import json
from collections.abc import AsyncGenerator
from typing import Optional

import httpx

from app.core.config import get_settings
from app.services.retrieval import RetrievalService


class AIAgent:
    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.settings = get_settings()
        self.retrieval_service = retrieval_service

    async def _chat(self, system: str, user: str) -> str:
        if not self.settings.ai_api_key:
            return self._fallback(system, user)

        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        }
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_with_rag(self, system: str, user: str, user_id: int) -> str:
        """带 RAG 上下文的聊天"""
        context = ""
        if self.retrieval_service:
            relevant_chunks = await self.retrieval_service.search(
                user, user_id, top_k=3
            )
            if relevant_chunks:
                context = "\n---\n".join(relevant_chunks)

        enriched_system = system
        if context:
            enriched_system = f"{system}\n\n以下是候选人的相关资料：\n{context}"

        return await self._chat(enriched_system, user)

    async def stream_chat(self, system: str, user: str) -> AsyncGenerator[str, None]:
        if not self.settings.ai_api_key:
            for chunk in self._fallback(system, user).split("，"):
                if chunk:
                    yield chunk + "，"
            return

        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line.removeprefix("data: ")
                    if raw == "[DONE]":
                        break
                    delta = json.loads(raw)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta

    async def generate_questions(
        self, focus: str, count: int, user_id: int
    ) -> list[dict]:
        """生成面试题（基于 RAG）"""
        system = f"""你是面试题设计专家。根据候选人的简历和 JD，生成 {count} 道面试题。
每道题包含：category, difficulty(easy/medium/hard), prompt, rubric(评分标准)。
输出 JSON 数组。"""

        result = await self._chat_with_rag(system, f"训练重点：{focus}", user_id)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # 降级到固定模板
            return self._fallback_questions(focus, count)

    async def score_answer(self, question: str, answer: str, user_id: int) -> dict:
        """评分回答（基于 RAG）"""
        system = """你是一位资深面试官，请从以下4个维度对候选人的回答评分（0-100）：
- clarity: 表达清晰度
- structure: 结构化程度（STAR）
- evidence: 证据和数据充分度
- reflection: 复盘和反思深度

严格按 JSON 格式输出：
{"score": 总分, "dimensions": {"clarity": 分, "structure": 分, "evidence": 分, "reflection": 分}, "summary": "一句话总结", "strengths": ["优点1"], "improvements": ["改进1"], "follow_up": "追问"}"""

        result = await self._chat_with_rag(
            system, f"题目：{question}\n回答：{answer}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_score()

    async def build_report(self, title: str, turns: list[dict], user_id: int) -> dict:
        """构建报告（基于 RAG）"""
        joined = "\n".join(
            f"Q:{turn['question']}\nA:{turn['answer']}" for turn in turns
        )

        system = """你是面试复盘教练，请输出中文 STAR Feedback 报告。
报告包含：
1. 整体评价
2. 各维度平均分（clarity, structure, evidence, reflection）
3. 改进建议
4. 下一步行动计划

输出 JSON 格式。"""

        result = await self._chat_with_rag(
            system, f"{title}\n{joined[:6000]}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_report(title, turns)

    async def build_roadmap(
        self, resume_text: str, jd_text: str, target_role: str, user_id: int
    ) -> dict:
        """构建路线图（基于 RAG）"""
        prompt = f"候选人简历：{resume_text[:2500]}\n岗位 JD：{jd_text[:2500]}\n目标岗位：{target_role}"
        content = await self._chat_with_rag(
            "你是中文 AI 面试教练，请输出简洁的准备路线。", prompt, user_id
        )
        return {
            "summary": content[:900],
            "milestones": ["岗位匹配分析", "高频题训练", "STAR 表达打磨", "模拟面试复盘"],
            "focusAreas": ["业务理解", "项目深挖", "结构化表达", "反问准备"],
        }

    async def generate_answer_cards(self, questions: list[dict], user_id: int) -> list[dict]:
        """为每道题生成 STAR 参考回答框架和关键词提示"""
        q_list = "\n".join(f"{i+1}. {q['prompt']}" for i, q in enumerate(questions[:6]))
        system = """你是面试教练，请为每道面试题生成参考回答框架。
输出 JSON 数组，每个元素包含：
- question: 原题
- star_hint: STAR 结构提示（简要说明每步怎么讲）
- keywords: 关键词列表（3-5 个）
- sample_opening: 参考开头句"""
        result = await self._chat_with_rag(system, f"请为以下面试题生成话术卡片：\n{q_list}", user_id)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_cards(questions)

    def _fallback_cards(self, questions: list[dict]) -> list[dict]:
        """话术卡片降级方案"""
        return [
            {
                "question": q.get("prompt", ""),
                "star_hint": "S: 描述背景 → T: 明确任务 → A: 展示行动 → R: 量化结果",
                "keywords": ["STAR 结构", "量化数据", "反思总结"],
                "sample_opening": "让我分享一个相关的项目经历...",
            }
            for q in questions[:6]
        ]

    async def coach_with_context(self, message: str, context: dict) -> str:
        return await self._chat(
            self.assistant_system_prompt(),
            self.assistant_user_prompt(message, context),
        )

    async def stream_coach_with_context(
        self, message: str, context: dict
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.stream_chat(
            self.assistant_system_prompt(),
            self.assistant_user_prompt(message, context),
        ):
            yield chunk

    async def analyze_resume(self, content: str, user_id: int) -> dict:
        """简历诊断评分：分析简历各模块质量并给出改进建议"""
        system = """你是一位资深简历顾问，请对候选人的简历进行全面诊断。
输出 JSON 格式：
{
  "overall_score": 总分(0-100),
  "modules": [
    {"name": "模块名称", "score": 分数(0-100), "comment": "一句话评价"}
  ],
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}
模块至少包含：教育背景、工作经历、项目经验、技能清单。
评分标准：量化数据、STAR 结构、关键词覆盖、排版清晰度。"""

        result = await self._chat_with_rag(
            system, f"请诊断以下简历内容：\n{content[:6000]}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_analysis()

    async def extract_jd_keywords(self, jd_content: str, user_id: int) -> dict:
        """从 JD 中提取结构化关键词"""
        system = """你是一位岗位分析专家，请从职位描述中提取关键要求。
输出 JSON 格式：
{
  "keywords": [
    {"term": "关键词", "category": "技术/软技能/经验/学历", "importance": "high/medium/low"}
  ]
}
提取 10-20 个关键词，按重要度排序。"""

        result = await self._chat_with_rag(
            system, f"请分析以下职位描述：\n{jd_content[:4000]}", user_id
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return self._fallback_keywords(jd_content)

    def _fallback_analysis(self) -> dict:
        """简历诊断降级方案"""
        return {
            "overall_score": 65,
            "modules": [
                {"name": "教育背景", "score": 70, "comment": "信息完整"},
                {"name": "工作经历", "score": 60, "comment": "缺少量化数据"},
                {"name": "项目经验", "score": 65, "comment": "建议补充 STAR 结构"},
                {"name": "技能清单", "score": 65, "comment": "覆盖面一般"},
            ],
            "issues": ["建议补充更多量化成果", "项目描述缺少 STAR 结构"],
            "suggestions": ["用数据量化工作成果", "按 STAR 结构重写项目经历"],
        }

    def _fallback_keywords(self, jd_content: str) -> dict:
        """关键词提取降级方案：简单分词"""
        import re
        words = re.findall(r'[一-鿿]{2,}|[A-Za-z][A-Za-z+#.]{2,}', jd_content)
        seen: set[str] = set()
        keywords: list[dict] = []
        for word in words:
            if word not in seen and len(word) >= 2:
                seen.add(word)
                keywords.append({"term": word, "category": "技术", "importance": "medium"})
            if len(keywords) >= 15:
                break
        return {"keywords": keywords}

    def assistant_system_prompt(self) -> str:
        return (
            "你是 InterviewPilot 的 AI 面试准备教练。你只能围绕求职面试准备提供帮助："
            "简历与 JD 匹配、题库训练、模拟面试、STAR 表达、复盘报告和下一步行动。"
            "回答要具体、可执行、中文优先；如果上下文不足，引导用户上传简历与 JD。"
        )

    def assistant_user_prompt(self, message: str, context: dict) -> str:
        return f"用户问题：{message}\n\n当前用户上下文：\n{json.dumps(context, ensure_ascii=False, default=str)[:8000]}"

    def _fallback(self, system: str, user: str) -> str:
        return (
            "这是 InterviewPilot 的本地模拟 AI 输出。建议先上传简历与 JD，生成准备计划后再开始题库训练。"
            "如果已经有材料，可以优先选择 3 个最匹配岗位要求的项目，按 STAR 结构准备：背景、任务、行动、结果。"
            "下一步建议：补齐岗位信息、生成 6 道高频题、完成一轮文字模拟面试，并用复盘报告修正表达。"
        )

    def _fallback_questions(self, focus: str, count: int) -> list[dict]:
        prompts = [
            f"请结合 {focus} 讲一个最能体现你解决复杂问题的项目。",
            "如果面试官质疑你的项目影响力，你会如何用数据回应？",
            "描述一次你和团队意见不一致时的处理方式。",
            "请解释你最近一个项目中的关键技术或业务取舍。",
            "如果入职后 30 天内要交付结果，你会如何拆解计划？",
            "你有哪些短板？最近如何系统改进？",
        ]
        return [
            {
                "category": focus,
                "difficulty": "medium" if i % 3 else "hard",
                "prompt": prompts[i % len(prompts)],
                "rubric": {"clarity": 25, "structure": 25, "evidence": 25, "reflection": 25},
            }
            for i in range(count)
        ]

    def _fallback_score(self) -> dict:
        return {
            "score": 70,
            "dimensions": {
                "clarity": 70,
                "structure": 70,
                "evidence": 70,
                "reflection": 70,
            },
            "summary": "回答已覆盖核心问题，建议补充更明确的行动、量化结果和复盘。",
            "strengths": ["回答完整"],
            "improvements": ["可以更具体", "需要量化"],
            "follow_up": "能否补充一个具体指标？",
        }

    def _fallback_report(self, title: str, turns: list[dict]) -> dict:
        return {
            "title": title,
            "overall": "整体表现良好，建议加强结构化表达。",
            "average_scores": {
                "clarity": 75,
                "structure": 70,
                "evidence": 72,
                "reflection": 68,
            },
            "improvements": ["使用 STAR 结构", "补充量化数据", "加强复盘深度"],
            "next_steps": ["练习高频题", "准备项目案例", "模拟面试"],
        }
