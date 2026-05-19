from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GrandPlatform"
    APP_NAME: str = "GrandPlatform"

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/grandplatform"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    STRIPE_SECRET_KEY: str = "sk_test_mock"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_mock"
    STRIPE_WEBHOOK_SECRET: str = "whsec_mock"

    ANTHROPIC_API_KEY: str = "mock_key"
    SENDGRID_API_KEY: str = "mock_key"
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = "mock_key"
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "mock_key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
