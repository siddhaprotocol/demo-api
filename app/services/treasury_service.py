"""
Treasury service for retrieving metrics data.
"""

from app.core.logging import get_logger
from app.schemas.treasury_schemas import TreasuryMetrics
from app.services.caching_service import redis_cache

logger = get_logger(__name__)

# Cache constants
TREASURY_METRICS_CACHE_KEY = "treasury:metrics"
TREASURY_METRICS_CACHE_TTL = 3600  # 1 hour in seconds


class TreasuryService:
    """Service for Treasury related operations."""

    @staticmethod
    def get_treasury_metrics() -> TreasuryMetrics:
        """
        Get treasury metrics (TVL and APY).

        Currently returns constant values. In a real implementation,
        this would fetch data from a database or external service.

        Returns:
            TreasuryMetrics: Treasury metrics including TVL and APY
        """
        # Check cache first
        cached_data = redis_cache.get_json(TREASURY_METRICS_CACHE_KEY)
        if cached_data:
            logger.info("Retrieved treasury metrics from cache")
            return TreasuryMetrics(**cached_data)

        # If not in cache, use constant values (in real implementation, would fetch from a source)
        metrics = TreasuryMetrics(tvl=1480000, apy=9.2)

        # Cache the result
        redis_cache.set_json(
            TREASURY_METRICS_CACHE_KEY, metrics.model_dump(), TREASURY_METRICS_CACHE_TTL
        )

        logger.info("Generated new treasury metrics")
        return metrics
