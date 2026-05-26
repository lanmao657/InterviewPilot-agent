# InterviewPilot Agent

AI 面试准备 Agent。前端使用 Vite + Vue 3 + TypeScript + shadcn-vue 风格组件，后端使用 FastAPI + PostgreSQL + Alembic。

## 功能

- 用户名密码注册/登录，JWT 鉴权，多用户数据隔离；邮箱字段保留以便未来重新启用邮箱能力
- 上传简历与 JD，生成准备计划和 Fit Score
- 生成面试题库
- 文字模拟面试、AI 追问、即时评分
- 生成 STAR Feedback 复盘报告
- OpenAI-compatible 模型接入；没有配置 `AI_API_KEY` 时会使用本地模拟输出跑通流程

## 本地启动

### 方式一：从根目录启动前端

```powershell
npm run dev
```

这个命令等价于：

```powershell
npm --prefix frontend run dev
```

### 方式二：进入前端目录启动

```powershell
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:5173`。

如果 `5173` 被占用，Vite 可能会自动切到 `http://localhost:5174`。后端默认允许 `5173-5179` 这一段本地开发端口访问。

## 启动后端

1. 复制环境变量：

```powershell
copy .env.example .env
```

2. 启动 PostgreSQL：

```powershell
docker compose up db
```

3. 启动 FastAPI：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

后端健康检查：`http://localhost:8000/health`。

修改 `.env` 中的 CORS 或模型配置后，需要重启 FastAPI 服务才会生效。

## CORS 配置

本地开发默认允许以下前端来源：

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5174`

同时默认允许 `localhost` / `127.0.0.1` 的 `5173-5179` 端口范围。生产部署时请在 `.env` 中显式设置 `CORS_ORIGINS` 和 `CORS_ORIGIN_REGEX`。

## Docker Compose

创建 `.env` 后可直接启动完整环境：

```powershell
docker compose up
```

## 测试

从根目录运行前端测试：

```powershell
npm test
```

或分别运行：

```powershell
cd frontend
npm test
```

```powershell
cd backend
pytest
```

## 常见问题

如果你在根目录运行 `npm run dev` 曾看到 `Could not read package.json`，说明当时根目录还没有代理脚本。现在根目录已经包含 `package.json`，可以直接运行 `npm run dev`。
