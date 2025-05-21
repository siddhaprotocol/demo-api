from pydantic import BaseModel, Field


class TreasuryMetrics(BaseModel):
    """
    Schema for Treasury metrics response.
    """

    tvl: float = Field(
        ..., description="Total Value Locked in the treasury", examples=[1480000]
    )
    apy: float = Field(..., description="Annual Percentage Yield", examples=[9.2])
