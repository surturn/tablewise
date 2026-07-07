import re

from pydantic import Field, model_validator
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
    SECRET_KEY: str = Field(repr=False)
    ALGORITHM: str = "HS256"
    CAPTCHA_ENABLED: bool = False
    HCAPTCHA_SECRET: str = Field(default="0x0000000000000000000000000000000000000000", repr=False)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ----------------------
    # POSTGRES
    # ----------------------
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = Field(repr=False)
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str = Field(repr=False)

    # ----------------------
    # REDIS
    # ----------------------
    REDIS_URL: str = ""

    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ----------------------
    # PAYMENTS (M-Pesa / Safaricom Daraja)
    # ----------------------
    MPESA_CONSUMER_KEY: str = Field(repr=False)
    MPESA_CONSUMER_SECRET: str = Field(repr=False)
    MPESA_SHORTCODE: str
    MPESA_PASSKEY: str = Field(repr=False)
    MPESA_CALLBACK_URL: str
    MPESA_ENV: str = "sandbox"

    # ----------------------
    # AI / EMAIL / SMS
    # ----------------------
    OPENAI_API_KEY: str = Field(repr=False)

    SENDGRID_API_KEY: str = Field(repr=False)

    AFRICASTALKING_USERNAME: str
    AFRICASTALKING_API_KEY: str = Field(repr=False)

    AT_USERNAME: str
    AT_API_KEY: str = Field(repr=False)

    # ──────────────────────────────────────────────
    # Computed URLs (normalised for Render compatibility)
    # ──────────────────────────────────────────────
    SYNC_DATABASE_URL: str = Field(default="", repr=False)

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