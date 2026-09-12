from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str
    postgres_user: str
    postgres_password: str

    elasticsearch_host: str

    batch_size: int = Field(default=100, gt=0)
    backoff_seconds: int = Field(default=5, gt=0)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "etl" / ".env",
        extra="ignore",
    )


settings = Settings()
