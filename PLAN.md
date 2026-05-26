# InterviewPilot 改进实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 InterviewPilot 从原型升级为具备 RAG pipeline、真正 AI 评分、工程化实践的成熟项目

**Architecture:** 基于 pgvector 实现向量检索，使用结构化 Prompt 实现 AI 评分，通过 FastAPI + Vue 3 + PostgreSQL 构建全栈应用

**Tech Stack:** FastAPI, Vue 3, PostgreSQL, pgvector, OpenAI API, ECharts, Docker, GitHub Actions

---

## Context

当前项目是一个 AI 面试准备平台的原型，存在以下核心问题使其无法写进简历：
- AI 调用只有 `chat/completions`，无 RAG/Embedding/向量检索
- 评分是假的：`min(95, max(45, 55 + len(answer) // 18))`（`ai_agent.py:92`）
- 题库是硬编码 6 个模板循环（`ai_agent.py:71-88`）
- Fit Score 是固定值 78/68（`prep_plans.py:30`）
- 报告 metrics 是硬编码 dict（`reports.py:36`）
- 文档摘要不是 AI 生成的（`documents.py:22-34`）
- 测试只有 2 个，无 CI/CD，无日志

改进目标：让项目具备 **RAG pipeline + 真正的 AI 评分 + 工程化实践**，可以在简历上展示为一个有技术深度的 AI 应用项目。

---

## 详细实施计划

**完整计划文档：** [docs/superpowers/plans/2026-05-27-interviewpilot-maturity.md](docs/superpowers/plans/2026-05-27-interviewpilot-maturity.md)

该计划包含：
1. **文件结构映射** — 明确每个文件的职责和修改范围
2. **咬合大小的任务** — 每个步骤 2-5 分钟可完成
3. **完整代码示例** — 无占位符，可直接执行
4. **具体命令和预期输出** — 确保执行无歧义
5. **自检清单** — 验证所有功能正常工作
6. **风险评估和备选方案** — 应对潜在问题
7. **时间估算和里程碑** — 11-16 天完成全部工作

---

## 快速开始

### 执行方式选择

**1. Subagent-Driven (推荐)** - 每个任务分派独立子代理，任务间审查，快速迭代

**2. Inline Execution** - 在当前会话中执行任务，批量执行带检查点

### 阶段概览

| 阶段 | 内容 | 时间估算 | 核心任务 |
|------|------|----------|----------|
| 一 | RAG 知识库 + 向量检索 | 3-4 天 | Task 1.1-1.6 |
| 二 | AI 评分和追问 | 2-3 天 | Task 2.1 |
| 三 | 报告增强 + 前端可视化 | 2-3 天 | Task 3.1 |
| 四 | 工程化补齐 | 2-3 天 | Task 4.1-4.2 |
| 五 | 产品增强 | 2-3 天 | 待规划 |

**总计：11-16 天**

---

## 验证清单

完成所有任务后，执行以下验证：

1. **RAG 验证：** 上传一份简历 → 提问"我在 XX 项目中用了什么技术" → 验证回答基于简历内容
2. **评分验证：** 提交一段回答 → 验证返回结构化评分 JSON（四维度分数 + 反馈）
3. **匹配度验证：** 上传简历+JD → 验证 Fit Score 不再是固定值
4. **测试验证：** `cd backend && pytest -v` 全部通过
5. **CI 验证：** push 到 GitHub 后 Actions 自动运行
6. **可视化验证：** 生成报告后查看雷达图和趋势图

---

## 改进后简历描述

> **InterviewPilot — AI 面试准备平台** | [https://github.com/lanmao657/InterviewPilot-agent](https://github.com/lanmao657/InterviewPilot-agent)
> - 基于 RAG 架构实现简历/JD 语义匹配与智能问答，使用 pgvector + Embedding 构建向量检索 pipeline
> - 设计四维度 AI 评分体系（清晰度/结构化/证据/复盘），通过 LLM 结构化输出实现量化评估
> - 构建文档解析 Pipeline，支持 PDF/DOCX 结构化提取、语义切片与岗位匹配度计算
> - 使用 FastAPI + Vue 3 + PostgreSQL 全栈开发，集成 GitHub Actions CI/CD + Docker 容器化部署
> - 实现 SSE 流式输出、语音输入、ECharts 数据可视化，优化面试模拟体验
