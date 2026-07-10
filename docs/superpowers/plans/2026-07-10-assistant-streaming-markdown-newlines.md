# AI 助手流式 Markdown 换行保真 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 AI 助手在流式生成期间就完整保留模型输出的 Markdown 换行和空行。

**Architecture:** 在 FastAPI 流路由中将每个逻辑增量编码为符合 SSE 规范的多行 `data:` 事件，前端继续使用现有 `parseSseBlock` 重组原始换行。不引入主动分段算法，不改变消息持久化、Markdown 渲染或错误处理流程。

**Tech Stack:** Python 3.10+、FastAPI `StreamingResponse`、pytest/pytest-asyncio、TypeScript、Vue 3、Pinia、Vitest。

---

## 文件职责

- `backend/app/routers/streams.py`：负责将 AI 文本增量、完成事件和错误事件编码为 SSE。
- `backend/tests/test_stream_errors.py`：验证 AI 助手流的安全错误输出与多行 Markdown 保真。
- `frontend/src/lib/api.test.ts`：锁定多行 `data:` 解析和 `streamApi` 回调的空行保真契约。

### Task 1: 修复后端 SSE 多行编码

**Files:**
- Modify: `backend/tests/test_stream_errors.py`
- Modify: `backend/app/routers/streams.py:57-86`

- [ ] **Step 1: 编写会失败的 AI 助手多行流回归测试**

在 `backend/tests/test_stream_errors.py` 追加：

```python
@pytest.mark.asyncio
async def test_assistant_stream_preserves_multiline_markdown_before_done(monkeypatch) -> None:
    class MultilineAgent:
        async def stream_coach_with_context(self, message: str, context: dict):
            yield "第一段\n\n第二段"

    finished: dict[str, str] = {}

    def capture_finish(_db, _conversation, _message, content: str, status: str) -> None:
        finished.update(content=content, status=status)

    monkeypatch.setattr(streams, "AIAgent", lambda: MultilineAgent())
    monkeypatch.setattr(streams, "finish_message", capture_finish)

    chunks = [
        chunk
        async for chunk in streams._sse_assistant_persisted(
            "请分段回答",
            {},
            db=object(),
            conversation=object(),
            assistant_message=object(),
        )
    ]

    assert chunks == [
        "data: 第一段\ndata: \ndata: 第二段\n\n",
        "event: done\ndata: [DONE]\n\n",
    ]
    assert finished == {"content": "第一段\n\n第二段", "status": "done"}
```

- [ ] **Step 2: 运行新用例并确认红灯**

Run from `backend`:

```powershell
pytest tests/test_stream_errors.py::test_assistant_stream_preserves_multiline_markdown_before_done -v
```

Expected: FAIL；第一个实际 chunk 是未编码的 `data: 第一段\n\n第二段\n\n`，与期望的多 `data:` 行不同。

- [ ] **Step 3: 实现最小 SSE 事件编码函数并复用到文本流**

在 `backend/app/routers/streams.py` 的 `_sse_text` 之前添加：

```python
def _format_sse_event(data: str, event: str | None = None) -> str:
    event_line = f"event: {event}\n" if event else ""
    data_lines = "".join(f"data: {line}\n" for line in data.split("\n"))
    return f"{event_line}{data_lines}\n"
```

将相关输出替换为：

```python
async def _sse_text(system: str, prompt: str):
    async for chunk in AIAgent().stream_chat(system, prompt):
        yield _format_sse_event(chunk)
    yield _format_sse_event("[DONE]", "done")


async def _sse_assistant_persisted(
    message: str,
    context: dict,
    db: Session,
    conversation: AssistantConversation,
    assistant_message: AssistantMessage,
):
    content = ""
    try:
        async for chunk in AIAgent().stream_coach_with_context(message, context):
            content += chunk
            yield _format_sse_event(chunk)
        finish_message(db, conversation, assistant_message, content, "done")
        yield _format_sse_event("[DONE]", "done")
    except asyncio.CancelledError:
        status = "done" if content else "error"
        finish_message(db, conversation, assistant_message, content or "助手回复已中断。", status)
        raise
    except Exception as exc:
        fallback = "助手暂时无法回答，请稍后重试。"
        content = content or fallback
        finish_message(db, conversation, assistant_message, content, "error")
        yield _format_sse_event(fallback, "error")
        yield _format_sse_event("[DONE]", "done")
```

- [ ] **Step 4: 运行后端流测试并确认绿灯**

Run from `backend`:

```powershell
pytest tests/test_stream_errors.py -v
```

Expected: 2 tests PASS，无失败。

- [ ] **Step 5: 提交后端修复与回归测试**

```powershell
git add backend/app/routers/streams.py backend/tests/test_stream_errors.py
git commit -m "fix: 保留 AI 助手流式 Markdown 换行"
```

### Task 2: 锁定前端 SSE 空行重组契约

**Files:**
- Modify: `frontend/src/lib/api.test.ts`

- [ ] **Step 1: 扩充解析用例并增加 `streamApi` 回调用例**

将导入更新为：

```typescript
import { parseSseBlock, streamApi, api } from './api'
```

将第一个 SSE 用例替换并在同一 `describe` 中追加回调用例：

```typescript
it('joins multiple data lines while preserving blank lines', () => {
  const event = parseSseBlock('event: message\ndata: 第一段\ndata: \ndata: 第二段')

  expect(event).toEqual({ event: 'message', data: '第一段\n\n第二段' })
})

it('delivers multiline chunks before the done event', async () => {
  setActivePinia(createPinia())
  const chunks: string[] = []
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
    'data: 第一段\ndata: \ndata: 第二段\n\nevent: done\ndata: [DONE]\n\n',
    { status: 200, headers: { 'Content-Type': 'text/event-stream' } },
  )))

  try {
    await streamApi('/stream/test', (chunk) => chunks.push(chunk))
  } finally {
    vi.unstubAllGlobals()
  }

  expect(chunks).toEqual(['第一段\n\n第二段'])
})
```

- [ ] **Step 2: 运行前端 API 契约测试**

Run from `frontend`:

```powershell
npm test -- src/lib/api.test.ts
```

Expected: `src/lib/api.test.ts` 全部用例 PASS，多行 chunk 回调中含两个原始换行。

- [ ] **Step 3: 提交前端协议回归测试**

```powershell
git add frontend/src/lib/api.test.ts
git commit -m "test: 补充 SSE 空行解析回归"
```

### Task 3: 全量验证与代码审查

**Files:**
- Verify: `backend`
- Verify: `frontend`
- Review: 本分支相对 `origin/codex/interviewpilot-bugfixes` 的完整差异

- [ ] **Step 1: 运行后端全量测试**

Run from `backend`:

```powershell
pytest
```

Expected: 全部用例 PASS，零失败。

- [ ] **Step 2: 运行前端全量测试和生产构建**

Run from `frontend`:

```powershell
npm test
npm run build
```

Expected: Vitest 零失败，`vue-tsc` 和 Vite 构建退出码均为 0。

- [ ] **Step 3: 对实现与规格进行独立审查**

审查必须确认：

```text
1. 每个换行分隔的物理行，包括空行，都编码为 data: 行。
2. 前端在 done 事件前已收到含空行的完整增量。
3. 持久化 content 与原始模型增量完全一致。
4. 错误、done 和心跳语义未改变。
5. 没有额外的主动分段或无关重构。
```

- [ ] **Step 4: 检查工作区和提交范围**

```powershell
git status --short
git diff --check origin/codex/interviewpilot-bugfixes...HEAD
git log --oneline origin/codex/interviewpilot-bugfixes..HEAD
```

Expected: 工作区为空，`git diff --check` 无输出，提交只包含设计、计划、SSE 修复和回归测试。

### Task 4: 同步远程并推送当前分支

**Files:**
- Push: `codex/interviewpilot-bugfixes`

- [ ] **Step 1: 获取远程分支并检查分叉**

```powershell
git fetch origin codex/interviewpilot-bugfixes
git rev-list --left-right --count HEAD...origin/codex/interviewpilot-bugfixes
```

Expected: 右侧计数为 `0`，表示本地不落后于远程；若不为 `0`，先停止推送并重新检查远程新增变更。

- [ ] **Step 2: 推送当前分支**

```powershell
git push origin HEAD:codex/interviewpilot-bugfixes
```

Expected: push 成功，远程 `origin/codex/interviewpilot-bugfixes` 指向当前 HEAD。
