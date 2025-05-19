"""
Configuration settings for the application.
"""

from typing import List

from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # API Settings
    allowed_origins: List[str] = Field(default=["*"])

    # Redis Settings
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str = Field(default="")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()