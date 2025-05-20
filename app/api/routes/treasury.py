"""
Treasury routes for metrics data.
"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.treasury_schemas import TreasuryMetrics
from app.services.treasury_service import TreasuryService

logger = get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["treasury"])


@router.get(
    "/treasury", response_model=TreasuryMetrics, operation_id="metrics/treasury/get"
)
async def get_treasury_metrics() -> TreasuryMetrics:
    """
    Get treasury metrics.
    - Returns current TVL (Total Value Locked) and APY (Annual Percentage Yield)
    - Cached in Redis for 1 hour
    - Example response: {"tvl": 1480000, "apy": 9.2}
    """
    return TreasuryService.get_treasury_metrics()
