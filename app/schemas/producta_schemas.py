"""
Pydantic schemas for Producta-related data.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ProductaStatus(BaseModel):
    """
    Pydantic model for Producta agent status.
    """

    status: Literal["done", "processing"] = Field(
        default="processing", description="Producta agent cron job status"
    )
