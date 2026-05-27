# InterviewPilot 登录系统重构设计规范

## 概述

本文档定义了 InterviewPilot 登录系统的重构方案，核心目标是添加游客登录功能，让用户无需注册即可完整体验平台功能。

**设计目标**：
- 添加游客登录选项（纯本地模式）
- 改善登录/注册体验
- 统一认证流程
- 保持与现有系统的兼容性

**技术栈**：
- 后端：FastAPI + SQLAlchemy + JWT
- 前端：Vue 3 + Pinia + localStorage

---

## 1. 设计原则

| 原则 | 描述 |
|------|------|
| **无感体验** | 游客点击即可进入，无需填写任何信息 |
| **完整功能** | 游客可以使用所有功能，包括 AI 助手、模拟面试等 |
| **数据隔离** | 游客数据与正式用户数据完全隔离 |
| **平滑过渡** | 游客可以随时注册正式账号 |

---

## 2. 后端设计

### 2.1 User 模型扩展

在 `backend/app/models/domain.py` 的 User 模型中添加 `is_anonymous` 字段：

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), default="候选人")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_anonymous: Mapped[bool] = mapped_column(default=False)  # 新增：标识是否为匿名用户
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 关系保持不变
    documents: Mapped[list["Document"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    prep_plans: Mapped[list["PrepPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    interviews: Mapped[list["InterviewSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    assistant_conversations: Mapped[list["AssistantConversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
```

### 2.2 Alembic 迁移

创建迁移文件添加 `is_anonymous` 字段：

```python
# backend/alembic/versions/xxx_add_is_anonymous_to_users.py
def upgrade():
    op.add_column('users', sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('users', 'is_anonymous')
```

### 2.3 新增游客登录接口

在 `backend/app/routers/auth.py` 中添加：

```python
import uuid

@router.post("/guest", response_model=TokenPair)
def guest_login(db: Session = Depends(get_db)) -> TokenPair:
    """游客登录：自动创建匿名用户"""
    guest_id = str(uuid.uuid4())[:8]
    username = f"guest_{guest_id}"
    
    user = User(
        username=username,
        email=None,
        name=f"游客 {guest_id}",
        hashed_password=hash_password(uuid.uuid4().hex),  # 随机密码，游客不需要知道
        is_anonymous=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_pair(user)
```

### 2.4 游客数据清理（可选，后续实现）

创建定时任务，清理 7 天前的匿名用户数据：

```python
# backend/app/tasks/cleanup_guests.py
from datetime import datetime, timedelta
from sqlalchemy import delete
from app.models import User
from app.core.database import get_db

def cleanup_old_guests():
    """清理 7 天前的匿名用户"""
    cutoff = datetime.utcnow() - timedelta(days=7)
    db = next(get_db())
    db.execute(delete(User).where(User.is_anonymous == True, User.created_at < cutoff))
    db.commit()
```

---

## 3. 前端设计

### 3.1 API 层更新

在 `frontend/src/lib/api.ts` 中添加游客登录接口：

```typescript
export const api = {
  // 现有接口...
  guestLogin: () => request<TokenPair>('/auth/guest', { method: 'POST', auth: false }),
  // ...
}
```

### 3.2 Auth Store 更新

在 `frontend/src/stores/auth.ts` 中添加游客标识：

```typescript
type AuthState = {
  accessToken: string
  refreshToken: string
  user: User | null
  isGuest: boolean  # 新增：标识是否为游客
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => {
    const stored = localStorage.getItem('interviewpilot-auth')
    const initialState = stored ? JSON.parse(stored) : { accessToken: '', refreshToken: '', user: null }
    return { ...initialState, isGuest: false }
  },
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

### 3.3 LoginPage.vue 重构

登录页面布局调整：

```
┌────────────────────────────────────────────────────┐
│                                                    │
│    ┌────────────────────────────────────────┐      │
│    │                                        │      │
│    │   🎯 InterviewPilot                   │      │
│    │   AI 面试准备平台                       │      │
│    │                                        │      │
│    │   ┌──────────────────────────────┐    │      │
│    │   │ 用户名                       │    │      │
│    │   └──────────────────────────────┘    │      │
│    │   ┌──────────────────────────────┐    │      │
│    │   │ 密码                         │    │      │
│    │   └──────────────────────────────┘    │      │
│    │                                        │      │
│    │   [登录]  [游客体验]                   │      │
│    │                                        │      │
│    │   没有账号？注册                       │      │
│    │                                        │      │
│    └────────────────────────────────────────┘      │
│                                                    │
└────────────────────────────────────────────────────┘
```

**关键代码**：

```vue
<script setup lang="ts">
import { Loader2, UserX } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isRegister = ref(false)
const loading = ref(false)
const guestLoading = ref(false)
const error = ref('')
const form = ref({ username: 'demo', password: 'password123' })

// ... 其他验证函数保持不变

async function guestLogin() {
  guestLoading.value = true
  error.value = ''
  try {
    const session = await api.guestLogin()
    auth.setSession(session, true)  // isGuest = true
    router.push('/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '游客登录失败'
  } finally {
    guestLoading.value = false
  }
}
</script>

<template>
  <main class="relative grid min-h-screen place-items-center overflow-hidden px-4 py-10">
    <!-- 背景装饰 -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-[var(--primary)]/10 blur-3xl" />
      <div class="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-[var(--accent)]/10 blur-3xl" />
    </div>

    <!-- 主题切换 -->
    <div class="absolute right-4 top-4">
      <ThemeToggle />
    </div>

    <!-- 登录卡片 -->
    <div class="glass-elevated w-full max-w-md rounded-2xl p-8 animate-fade-in-up">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 grid size-16 place-items-center rounded-2xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] text-2xl font-bold text-white shadow-lg">
          IP
        </div>
        <h1 class="text-2xl font-bold">InterviewPilot</h1>
        <p class="mt-1 text-sm text-[var(--text-secondary)]">AI 面试准备平台</p>
      </div>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <!-- 表单字段保持不变 -->

        <div class="flex gap-3">
          <Button type="submit" :disabled="loading" class="flex-1">
            <Loader2 v-if="loading" class="size-4 animate-spin" />
            {{ isRegister ? '注册并进入' : '登录' }}
          </Button>
          <Button type="button" variant="secondary" :disabled="guestLoading" @click="guestLogin" class="flex-1">
            <UserX v-if="!guestLoading" class="size-4" />
            <Loader2 v-else class="size-4 animate-spin" />
            游客体验
          </Button>
        </div>

        <Button type="button" variant="ghost" @click="toggleRegister">
          {{ isRegister ? '已有账号，去登录' : '没有账号，创建一个' }}
        </Button>
      </form>
    </div>
  </main>
</template>
```

### 3.4 游客提示横幅

在 `frontend/src/components/layout/AppShell.vue` 中添加游客提示：

```vue
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <!-- 游客提示横幅 -->
    <div v-if="auth.isGuest" class="glass border-b border-[var(--warning)]/30 bg-[var(--warning)]/10 px-4 py-2 text-center text-sm">
      <span class="text-[var(--warning)]">⚠️ 当前为游客模式</span>
      <span class="mx-2 text-[var(--text-muted)]">·</span>
      <span class="text-[var(--text-secondary)]">数据仅在本次会话中保存</span>
      <Button variant="ghost" size="sm" class="ml-3" @click="router.push('/login')">
        注册正式账号
      </Button>
    </div>

    <!-- 其余布局保持不变 -->
  </div>
</template>
```

---

## 4. 认证流程

### 4.1 正常登录流程

```
用户输入用户名密码 → POST /auth/login → 返回 TokenPair → 前端存储 → 跳转 Dashboard
```

### 4.2 游客登录流程

```
用户点击"游客体验" → POST /auth/guest → 后端创建匿名用户 → 返回 TokenPair → 前端存储（isGuest=true） → 跳转 Dashboard
```

### 4.3 游客升级流程（可选，后续实现）

```
游客点击"注册正式账号" → 跳转注册页面 → 填写信息 → POST /auth/register → 后端更新用户（is_anonymous=false） → 前端更新状态（isGuest=false）
```

---

## 5. 数据隔离

### 5.1 游客数据标识

所有游客创建的数据（文档、计划、面试记录等）都关联到 `is_anonymous=true` 的用户。

### 5.2 数据清理策略

- **自动清理**：定时任务清理 7 天前的匿名用户数据
- **手动清理**：管理员可以手动清理匿名用户
- **不清理**：保留匿名用户数据，但标记为"游客数据"

---

## 6. 安全考虑

### 6.1 游客限制

- 游客不能修改密码
- 游客不能修改邮箱
- 游客不能删除账号

### 6.2 游客数据保护

- 游客数据与其他用户隔离
- 游客不能访问其他用户的数据

---

## 7. 用户体验

### 7.1 登录页面

- 游客按钮与登录按钮并排显示
- 游客按钮使用次要样式（variant="secondary"）
- 点击后显示加载状态

### 7.2 应用内提示

- 顶部显示游客模式提示横幅
- 提示用户数据仅在本次会话保存
- 提供"注册正式账号"按钮

### 7.3 退出登录

- 游客退出登录时清除本地状态
- 不需要特殊处理匿名用户

---

## 8. 实施阶段

### 阶段一：后端实现（1 天）
1. User 模型添加 `is_anonymous` 字段
2. 创建 Alembic 迁移
3. 实现 `/auth/guest` 接口
4. 测试接口

### 阶段二：前端实现（1 天）
1. 更新 API 层
2. 更新 Auth Store
3. 重构 LoginPage.vue
4. 添加游客提示横幅

### 阶段三：测试与优化（0.5 天）
1. 测试游客登录流程
2. 测试游客功能访问
3. 优化用户体验

**总预计时间：2.5 天**

---

## 9. 验证清单

完成所有任务后，执行以下验证：

- [ ] 游客可以点击"游客体验"按钮进入系统
- [ ] 游客可以使用所有功能（文档、题库、面试、报告、AI 助手）
- [ ] 游客模式下显示提示横幅
- [ ] 游客可以正常退出登录
- [ ] 游客数据与其他用户隔离
- [ ] 正常用户登录流程不受影响
- [ ] 注册流程不受影响
- [ ] 所有测试通过

---

## 10. 未来扩展

### 10.1 游客数据迁移

允许游客注册正式账号时迁移数据：

```python
@router.post("/upgrade-guest", response_model=TokenPair)
def upgrade_guest(payload: UserCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """将游客账号升级为正式账号"""
    if not user.is_anonymous:
        raise HTTPException(status_code=400, detail="非游客账号")
    
    # 检查用户名是否已存在
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="用户名已注册")
    
    # 更新用户信息
    user.username = payload.username
    user.email = payload.email.lower() if payload.email else None
    user.name = payload.username
    user.hashed_password = hash_password(payload.password)
    user.is_anonymous = False
    
    db.commit()
    return _token_pair(user)
```

### 10.2 游客数据导出

允许游客导出自己的数据：

```python
@router.get("/export")
def export_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """导出用户数据"""
    return {
        "documents": [doc.to_dict() for doc in user.documents],
        "plans": [plan.to_dict() for plan in user.prep_plans],
        "interviews": [interview.to_dict() for interview in user.interviews],
    }
```

---

**文档版本**：1.0
**创建日期**：2026-05-27
**作者**：AI Assistant
