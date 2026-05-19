from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TableWise"

    # Security
    SECRET_KEY: str = "development_secret_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://tablewise_user:tablewise_password@localhost:5432/tablewise_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Stripe (primary card gateway, USD)
    STRIPE_SECRET_KEY: str = "mock_key"
    STRIPE_WEBHOOK_SECRET: str = "mock_key"
    PUBLIC_APP_URL: str = "http://localhost:5173"

    # Mobile money (fallback/market-local integrations)
    MOBILE_MONEY_PROVIDERS: list[str] = ["africas_talking", "mpesa"]
    MOBILE_MONEY_COLLECTION_URL: str = ""
    MOBILE_MONEY_CALLBACK_URL: str = ""
    MOBILE_MONEY_API_KEY: str = "mock_key"

    # Legacy M-Pesa compatibility
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CONSUMER_KEY: str = "mock_key"
    MPESA_CONSUMER_SECRET: str = "mock_key"
    MPESA_PASSKEY: str = "mock_key"
    MPESA_SHORTCODE: str = "174379"
    MPESA_CALLBACK_URL: str = ""

    # Offline-first controls
    OFFLINE_ORDER_ID_PREFIX: str = "offline"
    OFFLINE_SYNC_BATCH_SIZE: int = 100

    # External APIs
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "mock_key"
    OPENAI_API_KEY: str = "mock_key"
    AI_MIN_CONFIDENCE_SCORE: float = 0.70

    @field_validator("MOBILE_MONEY_PROVIDERS", mode="before")
    @classmethod
    def parse_mobile_money_providers(cls, value):
        if isinstance(value, str):
            return [provider.strip() for provider in value.split(",") if provider.strip()]
        return value

    # Pydantic v2 syntax for reading from .env
    model_config = SettingsConfigDict(
        # Changed from "../.env" to ".env" because it's now in the backend root
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()