from pydantic_settings import BaseSettings, SettingsConfigDict


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
    ]

    # ----------------------
    # SECURITY
    # ----------------------
    SECRET_KEY: str = "dev-secret-change-me"
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
    REDIS_URL: str

    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ----------------------
    # PAYMENTS
    # ----------------------
    STRIPE_SECRET_KEY: str = "sk_test_mock"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_mock"
    STRIPE_WEBHOOK_SECRET: str = "whsec_mock"

    # ----------------------
    # AI / EMAIL / SMS
    # ----------------------
    ANTHROPIC_API_KEY: str = "mock_key"

    SENDGRID_API_KEY: str = "mock_key"

    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = "mock_key"

    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "mock_key"

    # ----------------------
    # Pydantic Config
    # ----------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()