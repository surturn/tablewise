import re

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_async_url(url: str) -> str:
    """
    Render (and Heroku) inject DATABASE_URL as:
        postgres://user:pass@host:5432/db
    or  postgresql://user:pass@host:5432/db

    SQLAlchemy ≥ 1.4 requires an explicit driver suffix.
    This helper rewrites to ``postgresql+asyncpg://...`` for the async engine.
    """
    return re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", url)


def _normalize_sync_url(url: str) -> str:
    """
    Return a *synchronous* URL for Alembic CLI (uses psycopg2 by default).
    Rewrites to ``postgresql://...`` (no driver suffix = psycopg2).
    """
    return re.sub(r"^postgres(ql)?(\+\w+)?://", "postgresql://", url)


class Settings(BaseSettings):
    # ----------------------
    # APP
    # ----------------------
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GrandPlatform"
    APP_NAME: str = "GrandPlatform"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://tablewise-ashy.vercel.app",
    ]

    # ----------------------
    # SECURITY
    # ----------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ----------------------
    # POSTGRES
    # ----------------------
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str

    # ----------------------
    # REDIS
    # ----------------------
    REDIS_URL: str = ""

    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ----------------------
    # PAYMENTS
    # ----------------------
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # ----------------------
    # AI / EMAIL / SMS
    # ----------------------
    ANTHROPIC_API_KEY: str

    SENDGRID_API_KEY: str

    AFRICASTALKING_USERNAME: str
    AFRICASTALKING_API_KEY: str

    AT_USERNAME: str
    AT_API_KEY: str

    # ──────────────────────────────────────────────
    # Computed URLs (normalised for Render compatibility)
    # ──────────────────────────────────────────────
    SYNC_DATABASE_URL: str = ""

    @model_validator(mode="after")
    def _fix_database_urls(self) -> "Settings":
        """
        Normalise DATABASE_URL coming from Render / Heroku so that:
        • DATABASE_URL      → uses ``postgresql+asyncpg://`` (for the async engine)
        • SYNC_DATABASE_URL → uses ``postgresql://``         (for Alembic CLI / psycopg2)
        """
        raw = self.DATABASE_URL
        self.DATABASE_URL = _normalize_async_url(raw)
        self.SYNC_DATABASE_URL = _normalize_sync_url(raw)
        return self

    # ----------------------
    # Pydantic Config
    # ----------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()