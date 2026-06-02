from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "InterviewPilot API"
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
    cors_origin_regex: str | None = r"^https?://(localhost|127\.0\.0\.1):517[3-9]$"

    database_url: str = "postgresql+psycopg://interviewpilot:interviewpilot@localhost:5432/interviewpilot"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 14

    ai_base_url: str = "https://api.deepseek.com/v1"
    ai_api_key: str | None = None
    ai_model: str = "deepseek-v4-pro"

    # Embedding 配置（独立于 chat，可使用不同服务商）
    embedding_base_url: str | None = None  # 为空时回退到 ai_base_url
    embedding_api_key: str | None = None   # 为空时回退到 ai_api_key
    embedding_model: str = "text-embedding-v4"
    embedding_dimensions: int = 1024

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
