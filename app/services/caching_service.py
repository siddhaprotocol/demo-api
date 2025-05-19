"""
Redis caching service.
"""

import json
from typing import Any, Optional

import redis
from redis.exceptions import RedisError

from app.config.settings import settings
from app.core.logging import get_logger
from app.errors.cache_errors import CacheConnectionError, CacheOperationError

logger = get_logger(__name__)


class RedisCacheService:
    _instance = None
    _client: redis.Redis | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()  # noqa: SLF001
        return cls._instance

    def _connect(self) -> None:
        try:
            self._client = redis.Redis(**settings.redis_kwargs)
            self._client.ping()
        except RedisError as exc:
            logger.error("Failed to connect to Redis: %s", exc, exc_info=True)
            self._client = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._connect()
            if self._client is None:
                raise CacheConnectionError("Could not establish cache connection.")
        return self._client

    def get(self, key: str) -> Optional[str]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        Raises:
            CacheConnectionError: If Redis connection fails
            CacheOperationError: If Redis operation fails
        """
        try:
            return self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to get from cache: {str(e)}")

    def set(self, key: str, value: str, ttl: int) -> None:
        """
        Set a value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Raises:
            CacheConnectionError: If Redis connection fails
            CacheOperationError: If Redis operation fails
        """
        try:
            self.client.setex(key, ttl, value)
        except RedisError as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to set in cache: {str(e)}")

    def get_json(self, key: str) -> Optional[Any]:
        """
        Get a JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value or None if not found

        Raises:
            CacheConnectionError: If Redis connection fails
            CacheOperationError: If Redis operation fails
        """
        data = self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to decode JSON from cache for key {key}: {str(e)}"
                )
                # Return None for invalid JSON rather than raising an error
                return None
        return None

    def set_json(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a JSON value in cache with TTL.

        Args:
            key: Cache key
            value: Value to serialize and cache
            ttl: Time to live in seconds

        Raises:
            CacheConnectionError: If Redis connection fails
            CacheOperationError: If Redis operation fails
        """
        try:
            json_value = json.dumps(value)
            self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to encode value to JSON for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to encode to JSON: {str(e)}")


# Global singleton instance
redis_cache = RedisCacheService()
