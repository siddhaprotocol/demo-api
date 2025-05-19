"""
Configuration settings for the application.
"""

from typing import Any, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # Redis connection
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Connection-pool tweaks
    redis_connection_pool_size: int = 10
    redis_connection_timeout: int = 5  # seconds

    # Handy helper so other modules don’t need to remember every kwarg
    @property
    def redis_kwargs(self) -> Dict[str, Any]:
        """Kwargs you can hand straight to redis-py."""
        return dict(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,
            socket_connect_timeout=self.redis_connection_timeout,
            max_connections=self.redis_connection_pool_size,
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
logger.info("Redis host=%s  port=%s", settings.redis_host, settings.redis_port)
