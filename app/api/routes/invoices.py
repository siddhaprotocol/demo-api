"""
Invoice routes for the mock invoice feed.
"""

from typing import List

from fastapi import APIRouter, Query

from app.constants.invoice_constants import DEFAULT_LIMIT, MAX_LIMIT, MIN_LIMIT
from app.core.logging import get_logger
from app.schemas.invoice_schemas import Invoice
from app.services.invoice_service import InvoiceService

logger = get_logger(__name__)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=List[Invoice], operation_id="invoices/get")
async def get_invoices(
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Number of invoices to return",
    )
) -> List[Invoice]:
    """
    Get a list of mock invoices.
    - Limits the number of returned invoices (default: 50, max: 100)
    - Returns the same set of invoices for the same limit value
    - Cached in Redis for 60 seconds
    """
    return InvoiceService.get_invoices(limit)
