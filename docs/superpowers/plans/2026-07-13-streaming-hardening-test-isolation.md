# 流式传输与测试隔离加固实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除测试误连开发数据库和生产 SSE 被代理缓冲的风险，并用真实增量测试保证 Markdown 换行在流结束前交付。

**Architecture:** pytest 根级配置在测试收集前锁定 SQLite，并在会话入口和破坏性数据库操作处设置双重安全门；Nginx 在现有 `/api` 代理位置关闭响应缓冲；前端用可控 `ReadableStream` 验证内容事件与结束事件的先后关系。改动保持在测试基础设施、生产代理配置和既有 SSE 回归测试内。

**Tech Stack:** Python 3、pytest、SQLAlchemy、Nginx、TypeScript、Vitest、WHATWG Streams

---

## 文件结构

- 新建 `backend/tests/conftest.py`：在测试模块收集前固定测试环境，并拒绝非 SQLite 测试会话。
- 修改 `backend/tests/test_app_startup.py`：验证 pytest 当前数据库引擎确实是 SQLite。
- 修改 `backend/tests/test_auth.py`：在 `drop_all` 前增加最后一道 SQLite 安全检查。
- 修改 `backend/tests/test_docker_compose.py`：验证生产 Nginx 的 `/api` 块关闭代理缓冲。
- 修改 `frontend/nginx.conf`：关闭 `/api` 的响应缓冲。
- 修改 `frontend/src/lib/api.test.ts`：验证内容回调发生在 `done` 之前且保留 Markdown 空行。

### Task 1: 隔离 pytest 数据库

**Files:**
- Create: `backend/tests/conftest.py`
- Modify: `backend/tests/test_app_startup.py`
- Modify: `backend/tests/test_auth.py`

- [ ] **Step 1: 写入失败的数据库隔离测试**

在 `backend/tests/test_app_startup.py` 增加：

```python
def test_test_suite_uses_isolated_sqlite_database() -> None:
    from app.core.database import engine

    assert engine.url.get_backend_name() == "sqlite"
```

- [ ] **Step 2: 仅运行安全的隔离测试并确认失败**

Run: `cd backend; pytest tests/test_app_startup.py::test_test_suite_uses_isolated_sqlite_database -v`

Expected: FAIL，实际数据库后端为 `postgresql`；此时不运行会调用 `drop_all` 的完整测试套件。

- [ ] **Step 3: 在测试收集前锁定 SQLite 并添加会话安全门**

创建 `backend/tests/conftest.py`：

```python
import os
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE = BACKEND_ROOT / "test.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""
os.environ["EMBEDDING_API_KEY"] = "test-key"


def pytest_sessionstart(session) -> None:
    del session

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.core.database import engine

    if engine.url.get_backend_name() != "sqlite":
        raise RuntimeError("测试数据库必须使用 SQLite，已拒绝启动测试。")
```

- [ ] **Step 4: 在破坏性操作前添加独立安全检查**

将 `backend/tests/test_auth.py` 的 `setup_module` 改为：

```python
def setup_module() -> None:
    if engine.url.get_backend_name() != "sqlite":
        raise RuntimeError("认证测试只允许清理 SQLite 测试数据库。")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 5: 运行隔离测试并确认通过**

Run: `cd backend; pytest tests/test_app_startup.py::test_test_suite_uses_isolated_sqlite_database -v`

Expected: PASS，数据库后端为 `sqlite`。

### Task 2: 禁止生产 Nginx 缓冲 SSE

**Files:**
- Modify: `backend/tests/test_docker_compose.py`
- Modify: `frontend/nginx.conf`

- [ ] **Step 1: 写入失败的生产代理配置测试**

在 `backend/tests/test_docker_compose.py` 增加：

```python
def test_production_nginx_disables_api_proxy_buffering() -> None:
    nginx = (PROJECT_ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
    api_location = nginx.split("location /api", maxsplit=1)[1].split("}", maxsplit=1)[0]

    assert "proxy_buffering off;" in api_location
```

- [ ] **Step 2: 运行配置测试并确认失败**

Run: `cd backend; pytest tests/test_docker_compose.py::test_production_nginx_disables_api_proxy_buffering -v`

Expected: FAIL，`location /api` 中尚无 `proxy_buffering off;`。

- [ ] **Step 3: 加入最小生产配置修复**

在 `frontend/nginx.conf` 的 `location /api` 内加入：

```nginx
        proxy_buffering off;
```

- [ ] **Step 4: 运行配置测试并确认通过**

Run: `cd backend; pytest tests/test_docker_compose.py::test_production_nginx_disables_api_proxy_buffering -v`

Expected: PASS。

### Task 3: 验证前端在结束事件前派发内容

**Files:**
- Modify: `frontend/src/lib/api.test.ts`

- [ ] **Step 1: 将预装载响应改为可控增量流**

用以下测试替换现有 `delivers multiline chunks before the done event`：

```typescript
it('delivers multiline chunks before the done event', async () => {
  setActivePinia(createPinia())
  const chunks: string[] = []
  const encoder = new TextEncoder()
  let controller!: ReadableStreamDefaultController<Uint8Array>
  let streamClosed = false
  const body = new ReadableStream<Uint8Array>({
    start(streamController) {
      controller = streamController
    },
  })
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
    body,
    { status: 200, headers: { 'Content-Type': 'text/event-stream' } },
  )))

  const request = streamApi('/stream/test', (chunk) => chunks.push(chunk))
  try {
    controller.enqueue(encoder.encode('data: 第一段\ndata: \ndata: 第二段\n\n'))
    await vi.waitFor(() => {
      expect(chunks).toEqual(['第一段\n\n第二段'])
    })

    controller.enqueue(encoder.encode('event: done\ndata: [DONE]\n\n'))
    controller.close()
    streamClosed = true
    await request
  } finally {
    if (!streamClosed) controller.close()
    vi.unstubAllGlobals()
  }
})
```

- [ ] **Step 2: 运行前端定向测试**

Run: `cd frontend; npm test -- src/lib/api.test.ts`

Expected: 该文件全部测试 PASS；若客户端等到流关闭才派发内容，`vi.waitFor` 会超时失败。

### Task 4: 全量验证并提交

**Files:**
- Verify: `backend/tests/`
- Verify: `frontend/src/`
- Verify: `frontend/nginx.conf`

- [ ] **Step 1: 单进程运行后端完整测试**

Run: `cd backend; pytest`

Expected: 测试完整结束且全部 PASS，不再等待 PostgreSQL 连接。

- [ ] **Step 2: 运行前端完整测试**

Run: `cd frontend; npm test`

Expected: 全部测试 PASS。

- [ ] **Step 3: 构建生产前端镜像内容**

Run: `cd frontend; npm run build`

Expected: 构建成功，无 TypeScript 或打包错误。

- [ ] **Step 4: 检查差异和空白错误**

Run: `git diff --check; git status --short; git diff --stat`

Expected: `git diff --check` 无输出；变更仅覆盖本计划列出的文件。

- [ ] **Step 5: 提交修复**

```powershell
git add -- backend/tests/conftest.py backend/tests/test_app_startup.py backend/tests/test_auth.py backend/tests/test_docker_compose.py frontend/nginx.conf frontend/src/lib/api.test.ts docs/superpowers/plans/2026-07-13-streaming-hardening-test-isolation.md
git commit -m "fix: 加固流式输出与测试数据库隔离"
```
