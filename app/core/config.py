from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os


class Settings(BaseSettings):
    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"  # значение по умолчанию

    # Redis
    REDIS_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # дефолт
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # дефолт

    # App
    ENVIRONMENT: str = "development"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(
        env_file=".env" if os.getenv("ENVIRONMENT") == "development" else None,
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
