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
