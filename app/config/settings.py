"""
Configuration settings for the application.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

load_dotenv(dotenv_path=Path(__file__).parent / f".env.{ENVIRONMENT}")


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # General
    environment: str = Field(default=ENVIRONMENT)
    cache_provider: str = Field(
        default="redis", description="Cache provider: 'redis' or 'valkey'"
    )

    # Cross-origin (unchanged, just showing it)
    allowed_origins: List[str] = Field(default=["*"])

    # Redis / Valkey connection
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

    model_config = ConfigDict(
        env_file=None,  # we already loaded the right file above
        case_sensitive=False,
    )


settings = Settings()
