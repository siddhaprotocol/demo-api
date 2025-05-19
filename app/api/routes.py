"""
API route definitions.
"""

from fastapi import APIRouter

from app.api.routes.invoices import router as invoices_router
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

router.include_router(invoices_router)
