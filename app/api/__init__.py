"""
API route definitions.
"""

from fastapi import APIRouter

from app.api.routes.agent_logs import router as agent_logs_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.producta import router as producta_router
from app.api.routes.treasury import router as treasury_router
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

router.include_router(invoices_router)
router.include_router(producta_router)
router.include_router(treasury_router)
router.include_router(agent_logs_router)
