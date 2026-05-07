import json
from collections.abc import AsyncGenerator

import httpx

from app.core.config import get_settings


class AIAgent:
    def __init__(self) -> None:
        self.settings = get_settings()

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
            response = await client.post(f"{self.settings.ai_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

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
            async with client.stream("POST", f"{self.settings.ai_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers) as response:
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

    async def build_roadmap(self, resume_text: str, jd_text: str, target_role: str) -> dict:
        prompt = f"候选人简历：{resume_text[:2500]}\n岗位 JD：{jd_text[:2500]}\n目标岗位：{target_role}"
        content = await self._chat("你是中文 AI 面试教练，请输出简洁的准备路线。", prompt)
        return {
            "summary": content[:900],
            "milestones": ["岗位匹配分析", "高频题训练", "STAR 表达打磨", "模拟面试复盘"],
            "focusAreas": ["业务理解", "项目深挖", "结构化表达", "反问准备"],
        }

    async def generate_questions(self, focus: str, count: int) -> list[dict]:
        prompts = [
            f"请结合 {focus} 讲一个最能体现你解决复杂问题的项目。",
            "如果面试官质疑你的项目影响力，你会如何用数据回应？",
            "描述一次你和团队意见不一致时的处理方式。",
            "请解释你最近一个项目中的关键技术或业务取舍。",
            "如果入职后 30 天内要交付结果，你会如何拆解计划？",
            "你有哪些短板？最近如何系统改进？",
        ]
        result = []
        for index in range(count):
            result.append(
                {
                    "category": focus,
                    "difficulty": "medium" if index % 3 else "hard",
                    "prompt": prompts[index % len(prompts)],
                    "rubric": {"clarity": 25, "structure": 25, "evidence": 25, "reflection": 25},
                }
            )
        return result

    async def score_answer(self, question: str, answer: str) -> dict:
        score = min(95, max(45, 55 + len(answer) // 18))
        return {
            "score": score,
            "feedback": {
                "summary": "回答已覆盖核心问题，建议补充更明确的行动、量化结果和复盘。",
                "star": {"situation": "可更具体", "task": "较清晰", "action": "需要量化", "result": "建议补充指标"},
                "nextQuestion": "能否补充一个具体指标，说明这个行动最终带来了什么变化？",
            },
        }

    async def build_report(self, title: str, turns: list[dict]) -> str:
        joined = "\n".join(f"Q:{turn['question']}\nA:{turn['answer']}" for turn in turns)
        return await self._chat("你是面试复盘教练，请输出中文 STAR Feedback 报告。", f"{title}\n{joined[:6000]}")

    async def coach_with_context(self, message: str, context: dict) -> str:
        return await self._chat(self.assistant_system_prompt(), self.assistant_user_prompt(message, context))

    async def stream_coach_with_context(self, message: str, context: dict) -> AsyncGenerator[str, None]:
        async for chunk in self.stream_chat(self.assistant_system_prompt(), self.assistant_user_prompt(message, context)):
            yield chunk

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
