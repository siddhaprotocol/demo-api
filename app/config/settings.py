"""
Configuration settings for the application.
"""

from typing import List, Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # API Settings
    allowed_origins: List[str] = Field(default=["*"])

    # Cache Provider Settings
    cache_provider: str = Field(
        default="redis", description="Cache provider: 'redis' or 'valkey'"
    )

    # Redis/Valkey Connection Settings
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str = Field(default="")

    # AWS ElastiCache specific settings
    aws_region: Optional[str] = Field(default=None)
    elasticache_tls_enabled: bool = Field(default=False)
    elasticache_ssl_cert_reqs: Optional[str] = Field(default=None)

    # Connection pool settings
    redis_connection_pool_size: int = Field(default=10)
    redis_connection_timeout: int = Field(default=5)  # seconds

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
