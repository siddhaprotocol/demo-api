"""
Producta routes for status management.
"""

from fastapi import APIRouter, Body

from app.core.logging import get_logger
from app.schemas.producta_schemas import ProductaStatus
from app.services.producta_service import ProductaService

logger = get_logger(__name__)

router = APIRouter(prefix="/producta", tags=["producta"])


@router.get(
    "/status", response_model=ProductaStatus, operation_id="producta/status/get"
)
async def get_producta_status() -> ProductaStatus:
    """
    Get the status of a Producta.
    - Returns the current status for the producta cron job
    - Stored in Redis cache for 10 minutes
    """
    return ProductaService.get_status()


@router.patch(
    "/status", response_model=ProductaStatus, operation_id="producta/status/update"
)
async def update_producta_status(
    status_update: ProductaStatus = Body(...),
) -> ProductaStatus:
    """
    Update the status of a Producta agent.
    - Updates the status for the producta cron job
    - Invalidates the cache for the producta status
    - Returns the updated status
    - Cached in Redis for 10 minutes
    - Example: {"status": "done"}
    - Example: {"status": "processing"}
    """
    return ProductaService.update_status(status_update)
