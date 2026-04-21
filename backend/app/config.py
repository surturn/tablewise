from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TableWise"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str
    REDIS_URL: str

    # M-Pesa
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CONSUMER_KEY: str
    MPESA_CONSUMER_SECRET: str
    MPESA_PASSKEY: str
    MPESA_SHORTCODE: str = "174379"
    MPESA_CALLBACK_URL: str

    # External APIs
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str
    OPENAI_API_KEY: str

    # Pydantic v2 syntax for reading from .env
    model_config = SettingsConfigDict(
        # Changed from "../.env" to ".env" because it's now in the backend root
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()