"""
Service for Producta-related functionality.
"""

from app.core.logging import get_logger
from app.schemas.producta_schemas import ProductaStatus
from app.services.caching_service import redis_cache

logger = get_logger(__name__)


class ProductaService:
    """Service for Producta operations."""

    _cache_key = "producta:status:"
    _cache_ttl = 600  # 10 minutes

    @classmethod
    def get_status(cls) -> ProductaStatus:
        """Get status for a Producta ID."""
        cache_key = cls._cache_key
        cached_status = redis_cache.get(cache_key)
        if cached_status is None:
            redis_cache.set(cache_key, "processing", cls._cache_ttl)
            return ProductaStatus(
                status="processing",
            )
        # Convert bytes to string if needed
        status_value = (
            cached_status.decode("utf-8")
            if isinstance(cached_status, bytes)
            else cached_status
        )
        return ProductaStatus(
            status=status_value,
        )

    @classmethod
    def update_status(cls, status_update: ProductaStatus) -> ProductaStatus:
        """Update status for agent Producta in redis cache."""

        updated_status = ProductaStatus(
            status=status_update.status,
        )
        redis_cache.set(cls._cache_key, updated_status.status, cls._cache_ttl)
        return updated_status
