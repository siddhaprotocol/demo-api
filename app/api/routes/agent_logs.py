"""
Agent logs routes for the demo activity ticker.
"""

from typing import List

from fastapi import APIRouter, Query

from app.constants.agent_logs_constants import DEFAULT_LIMIT, MAX_LIMIT, MIN_LIMIT
from app.core.logging import get_logger
from app.services.agent_logs_service import AgentLogsService

logger = get_logger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get(
    "/agent",
    response_model=List[str],
    operation_id="logs/agent/get",
    description="Get deterministic agent activity logs for the scrolling ticker",
)
async def get_agent_logs(
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Number of log messages to return",
    )
) -> List[str]:
    """
    Get a list of agent activity logs.
    - Provides deterministic log messages for the scrolling ticker
    - Limits the number of returned logs (default: 10, max: 20)
    - Returns the same set of logs for the same limit value
    - Cached in Redis for 30 seconds
    - p95 response time < 80ms from SF & NYC POPs
    """
    return AgentLogsService.get_agent_logs(limit)
