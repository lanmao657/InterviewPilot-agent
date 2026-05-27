# 登录系统重构 + 游客登录实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 InterviewPilot 登录系统中添加游客登录功能，用户点击"游客体验"即可创建匿名账号并完整使用所有功能。

**Architecture:** 后端新增 `/auth/guest` 接口，自动创建 `is_anonymous=True` 的匿名用户并返回 TokenPair；前端在 LoginPage 添加游客按钮，Auth Store 添加 `isGuest` 状态，AppShell 显示游客提示横幅。不修改现有登录/注册流程。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, Pinia, TypeScript, Tailwind CSS 4

**Design Spec:** `docs/superpowers/specs/2026-05-27-login-system-redesign.md`

---

## 文件结构映射

### 后端修改文件
- `backend/app/models/domain.py` — User 模型添加 `is_anonymous` 字段
- `backend/app/schemas.py` — UserRead 添加 `is_anonymous` 字段
- `backend/app/routers/auth.py` — 新增 `/auth/guest` 接口
- `backend/alembic/versions/` — 新增迁移文件

### 前端修改文件
- `frontend/src/lib/api.ts` — 添加 `guestLogin` 方法
- `frontend/src/stores/auth.ts` — 添加 `isGuest` 状态
- `frontend/src/pages/LoginPage.vue` — 添加游客按钮
- `frontend/src/components/layout/AppShell.vue` — 添加游客提示横幅

---

## 阶段一：后端实现

### Task 1.1: User 模型添加 is_anonymous 字段

**Files:**
- Modify: `backend/app/models/domain.py:21-36`

- [ ] **Step 1: 修改 User 模型**

在 `backend/app/models/domain.py` 的 User 类中，在 `hashed_password` 字段之后添加 `is_anonymous` 字段：

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), default="候选人")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_anonymous: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 关系保持不变
```

- [ ] **Step 2: 验证模型加载**

Run: `cd backend && python -c "from app.models import User; print(User.__table__.columns.keys())"`
Expected: 输出包含 `is_anonymous`

- [ ] **Step 3: 提交**

```bash
git add backend/app/models/domain.py
git commit -m "feat: User 模型添加 is_anonymous 字段"
```

---

### Task 1.2: 创建 Alembic 迁移

**Files:**
- Create: `backend/alembic/versions/xxx_add_is_anonymous_to_users.py`

- [ ] **Step 1: 生成迁移文件**

Run: `cd backend && alembic revision --autogenerate -m "add_is_anonymous_to_users"`
Expected: 生成迁移文件

- [ ] **Step 2: 检查迁移文件内容**

迁移文件应包含：

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'is_anonymous')
```

- [ ] **Step 3: 应用迁移**

Run: `cd backend && alembic upgrade head`
Expected: 迁移成功

- [ ] **Step 4: 提交**

```bash
git add backend/alembic/versions/
git commit -m "feat: 添加 is_anonymous 字段迁移"
```

---

### Task 1.3: 更新 UserRead Schema

**Files:**
- Modify: `backend/app/schemas.py:67-73`

- [ ] **Step 1: 修改 UserRead schema**

在 `backend/app/schemas.py` 的 UserRead 类中添加 `is_anonymous` 字段：

```python
class UserRead(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr | None = None
    is_anonymous: bool = False

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 验证 schema**

Run: `cd backend && python -c "from app.schemas import UserRead; print(UserRead.model_fields.keys())"`
Expected: 输出包含 `is_anonymous`

- [ ] **Step 3: 提交**

```bash
git add backend/app/schemas.py
git commit -m "feat: UserRead schema 添加 is_anonymous 字段"
```

---

### Task 1.4: 实现游客登录接口

**Files:**
- Modify: `backend/app/routers/auth.py`

- [ ] **Step 1: 编写测试**

```python
# backend/tests/test_auth_guest.py
import pytest


def test_guest_login_creates_anonymous_user(client):
    """测试游客登录创建匿名用户"""
    response = client.post("/api/auth/guest")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["is_anonymous"] is True
    assert data["user"]["username"].startswith("guest_")


def test_guest_login_returns_valid_token(client):
    """测试游客登录返回有效 token"""
    response = client.post("/api/auth/guest")
    token = response.json()["access_token"]
    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["is_anonymous"] is True


def test_guest_login_multiple_times_creates_different_users(client):
    """测试多次游客登录创建不同用户"""
    resp1 = client.post("/api/auth/guest")
    resp2 = client.post("/api/auth/guest")
    assert resp1.json()["user"]["id"] != resp2.json()["user"]["id"]
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd backend && pytest tests/test_auth_guest.py -v`
Expected: FAIL with 404 (接口不存在)

- [ ] **Step 3: 实现游客登录接口**

在 `backend/app/routers/auth.py` 中添加：

```python
import uuid

# 在文件顶部添加导入
from app.models import User
# ... 其他导入保持不变

@router.post("/guest", response_model=TokenPair)
def guest_login(db: Session = Depends(get_db)) -> TokenPair:
    """游客登录：自动创建匿名用户"""
    guest_id = str(uuid.uuid4())[:8]
    username = f"guest_{guest_id}"

    user = User(
        username=username,
        email=None,
        name=f"游客 {guest_id}",
        hashed_password=hash_password(uuid.uuid4().hex),
        is_anonymous=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_pair(user)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd backend && pytest tests/test_auth_guest.py -v`
Expected: 3 tests PASSED

- [ ] **Step 5: 运行所有后端测试确保无回归**

Run: `cd backend && pytest -v`
Expected: 所有测试通过

- [ ] **Step 6: 提交**

```bash
git add backend/app/routers/auth.py backend/tests/test_auth_guest.py
git commit -m "feat: 实现游客登录接口 /auth/guest"
```

---

## 阶段二：前端实现

### Task 2.1: API 层添加游客登录方法

**Files:**
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: 添加 guestLogin 方法**

在 `frontend/src/lib/api.ts` 的 `api` 对象中，在 `login` 方法之后添加：

```typescript
export const api = {
  register: (payload: { username: string; password: string; email?: string }) =>
    request<TokenPair>('/auth/register', { method: 'POST', body: JSON.stringify(payload), auth: false }),
  login: (payload: { username: string; password: string }) =>
    request<TokenPair>('/auth/login', { method: 'POST', body: JSON.stringify(payload), auth: false }),
  guestLogin: () =>
    request<TokenPair>('/auth/guest', { method: 'POST', auth: false }),
  me: () => request<User>('/auth/me'),
  // ... 其余保持不变
}
```

- [ ] **Step 2: 更新 User 类型**

在 `frontend/src/lib/api.ts` 的 User 类型中添加 `is_anonymous` 字段：

```typescript
export type User = { id: number; username: string; name: string; email: string | null; is_anonymous: boolean }
```

- [ ] **Step 3: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 4: 提交**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: API 层添加游客登录方法和 is_anonymous 类型"
```

---

### Task 2.2: Auth Store 添加游客状态

**Files:**
- Modify: `frontend/src/stores/auth.ts`

- [ ] **Step 1: 修改 AuthState 类型**

```typescript
type AuthState = {
  accessToken: string
  refreshToken: string
  user: User | null
  isGuest: boolean
}
```

- [ ] **Step 2: 修改 store 初始化**

```typescript
const stored = localStorage.getItem('interviewpilot-auth')
const initialState = stored ? (JSON.parse(stored) as Omit<AuthState, 'isGuest'>) : { accessToken: '', refreshToken: '', user: null }

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    ...initialState,
    isGuest: initialState.user?.is_anonymous ?? false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
    isGuestUser: (state) => state.isGuest,
  },
  actions: {
    setSession(session: TokenPair, isGuest = false) {
      this.accessToken = session.access_token
      this.refreshToken = session.refresh_token
      this.user = session.user
      this.isGuest = isGuest
      this.persist()
    },
    logout() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      this.isGuest = false
      this.persist()
    },
    persist() {
      localStorage.setItem(
        'interviewpilot-auth',
        JSON.stringify({
          accessToken: this.accessToken,
          refreshToken: this.refreshToken,
          user: this.user,
        }),
      )
    },
  },
})
```

- [ ] **Step 3: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/auth.ts
git commit -m "feat: Auth Store 添加 isGuest 状态"
```

---

### Task 2.3: LoginPage 添加游客按钮

**Files:**
- Modify: `frontend/src/pages/LoginPage.vue`

- [ ] **Step 1: 添加 UserX 图标导入**

```typescript
import { Loader2, UserX } from 'lucide-vue-next'
```

- [ ] **Step 2: 添加 guestLoading 状态和 guestLogin 函数**

```typescript
const guestLoading = ref(false)

async function guestLogin() {
  guestLoading.value = true
  error.value = ''
  try {
    const session = await api.guestLogin()
    auth.setSession(session, true)
    router.push('/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '游客登录失败'
  } finally {
    guestLoading.value = false
  }
}
```

- [ ] **Step 3: 修改表单按钮区域**

将原来的单个按钮改为并排双按钮：

```vue
<div class="flex gap-3">
  <Button type="submit" :disabled="loading" class="flex-1">
    <Loader2 v-if="loading" class="size-4 animate-spin" />
    {{ isRegister ? '注册并进入' : '登录' }}
  </Button>
  <Button type="button" variant="secondary" :disabled="guestLoading" class="flex-1" @click="guestLogin">
    <UserX v-if="!guestLoading" class="size-4" />
    <Loader2 v-else class="size-4 animate-spin" />
    游客体验
  </Button>
</div>
```

- [ ] **Step 4: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 5: 提交**

```bash
git add frontend/src/pages/LoginPage.vue
git commit -m "feat: LoginPage 添加游客体验按钮"
```

---

### Task 2.4: AppShell 添加游客提示横幅

**Files:**
- Modify: `frontend/src/components/layout/AppShell.vue`

- [ ] **Step 1: 添加 AlertTriangle 图标导入**

```typescript
import {
  AlertTriangle,
  BarChart3,
  BookOpenCheck,
  Bot,
  FileText,
  Gauge,
  LogOut,
  Menu,
  MessageSquareText,
  Settings,
  UserCircle,
  X,
} from 'lucide-vue-next'
```

- [ ] **Step 2: 在主内容区顶部添加游客提示横幅**

在 `<main>` 标签内部，`<header>` 之前添加：

```vue
<!-- 游客提示横幅 -->
<Transition name="fade">
  <div
    v-if="auth.isGuest"
    class="flex items-center justify-center gap-2 border-b border-[var(--warning)]/30 bg-[var(--warning)]/10 px-4 py-2 text-sm"
  >
    <AlertTriangle class="size-4 text-[var(--warning)]" />
    <span class="text-[var(--text-secondary)]">当前为游客模式，数据仅在本次会话中保存</span>
    <Button variant="ghost" size="sm" @click="router.push('/login')">
      注册正式账号
    </Button>
  </div>
</Transition>
```

- [ ] **Step 3: 验证构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/layout/AppShell.vue
git commit -m "feat: AppShell 添加游客模式提示横幅"
```

---

## 阶段三：测试与验证

### Task 3.1: 端到端验证

**Files:**
- 无新增文件

- [ ] **Step 1: 运行后端测试**

Run: `cd backend && pytest -v`
Expected: 所有测试通过

- [ ] **Step 2: 运行前端构建**

Run: `cd frontend && npm run build`
Expected: 构建成功

- [ ] **Step 3: 运行前端测试**

Run: `cd frontend && npx vitest run`
Expected: 所有测试通过

- [ ] **Step 4: 推送到远程仓库**

```bash
git push origin master
```

---

## 自检清单

完成所有任务后，执行以下验证：

- [ ] 游客可以点击"游客体验"按钮进入系统
- [ ] 游客可以使用所有功能（文档、题库、面试、报告、AI 助手）
- [ ] 游客模式下显示提示横幅
- [ ] 游客可以正常退出登录
- [ ] 游客数据与其他用户隔离
- [ ] 正常用户登录流程不受影响
- [ ] 注册流程不受影响
- [ ] `cd backend && pytest -v` 所有测试通过
- [ ] `cd frontend && npm run build` 构建成功
- [ ] `cd frontend && npx vitest run` 所有测试通过
