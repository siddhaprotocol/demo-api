"""
Redis caching service.
"""

import json
from typing import Any, Optional, TypeVar

import redis
from redis.exceptions import RedisError

from app.config.settings import settings
from app.core.logging import get_logger
from app.errors.cache_errors import CacheConnectionError, CacheOperationError

logger = get_logger(__name__)

T = TypeVar("T")


class RedisCacheService:
    """
    Service for interacting with Redis cache.
    """

    _instance = None
    _client = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(RedisCacheService, cls).__new__(cls)
            try:
                cls._client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True,
                )
                # Test connection
                cls._client.ping()
                logger.info("Connected to Redis cache")
            except RedisError as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
        return cls._instance

    @property
    def client(self) -> redis.Redis:
        """Get Redis client, reconnecting if necessary."""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True,
                )
                self._client.ping()
                logger.info("Reconnected to Redis cache")
            except RedisError as e:
                logger.error(f"Failed to reconnect to Redis: {str(e)}")
                raise CacheConnectionError(f"Failed to connect to Redis: {str(e)}")
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
