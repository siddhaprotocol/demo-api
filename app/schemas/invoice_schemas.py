"""
Pydantic schemas for invoice-related data.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Invoice(BaseModel):
    """Schema for a single invoice."""

    id: str = Field(..., description="Invoice ID in format INV-XXX-YYY")
    client: str = Field(..., description="Client company name")
    amount: int = Field(..., description="Invoice amount in whole dollars")
    risk: float = Field(..., description="Risk score between 0.005 and 0.080")
    tokenId: str = Field(..., description="Token ID in format TIQ-XXXX")
    status: Literal["new", "processing", "funded"] = Field(
        ..., description="Current invoice status"
    )
