from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional


class Settings(BaseSettings):
    # General
    app_env: str = "dev"
    app_name: str = "SamuraiTasks"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Database
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    # Redis
    redis_host: str
    redis_port: int
    redis_db: int

    # Worker
    stream_name: str
    consumer_group: str
    consumer_name: str
    consumer_port: int
    lock_ttl: int = 5000  # ms
    outbox_poll_interval: float = 0.5

    # 🪶 Logging
    log_level: str = "INFO"

    # Auto-generated URLs
    @computed_field
    @property
    def database_url(self) -> str:
        """Build database URL dynamically for SQLAlchemy/asyncpg"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def redis_url(self) -> str:
        """Build Redis connection URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unexpected vars instead of raising errors
    )


# Global settings instance
settings = Settings()
