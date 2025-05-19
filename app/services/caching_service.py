"""
Caching service for Redis and Valkey ElastiCache.
"""

import json
import ssl
from typing import Any, Dict, Optional, TypeVar

import redis
from redis.exceptions import RedisError

from app.config.settings import settings
from app.core.logging import get_logger
from app.errors.cache_errors import CacheConnectionError, CacheOperationError

logger = get_logger(__name__)

T = TypeVar("T")


class CacheService:
    """
    Service for interacting with Redis/Valkey cache.
    """

    _instance = None
    _client = None
    _connection_pool = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            try:
                connection_params = cls._get_connection_params()
                cls._connection_pool = redis.ConnectionPool(
                    **connection_params,
                    max_connections=settings.redis_connection_pool_size,
                )
                cls._client = redis.Redis(
                    connection_pool=cls._connection_pool,
                    socket_timeout=settings.redis_connection_timeout,
                    decode_responses=True,
                )
                # Test connection
                cls._client.ping()
                logger.info(
                    f"Connected to {settings.cache_provider.capitalize()} cache"
                )
            except RedisError as e:
                logger.error(
                    f"Failed to connect to {settings.cache_provider.capitalize()}: {str(e)}"
                )
                # Don't raise here to allow application to start even if cache is unavailable
                # Connection will be retried on next operation
        return cls._instance

    @staticmethod
    def _get_connection_params() -> Dict[str, Any]:
        """
        Get connection parameters based on configuration.

        Returns:
            Dictionary of connection parameters
        """
        connection_params = {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "password": settings.redis_password,
        }

        # Add SSL/TLS configuration for AWS ElastiCache if enabled
        if settings.elasticache_tls_enabled:
            ssl_context = ssl.create_default_context()

            # Configure SSL verification mode if specified
            if settings.elasticache_ssl_cert_reqs:
                if settings.elasticache_ssl_cert_reqs.lower() == "none":
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                elif settings.elasticache_ssl_cert_reqs.lower() == "optional":
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_OPTIONAL
                elif settings.elasticache_ssl_cert_reqs.lower() == "required":
                    ssl_context.check_hostname = True
                    ssl_context.verify_mode = ssl.CERT_REQUIRED

            # Use 'ssl' parameter instead of 'ssl_context' for Redis 5.0.4 compatibility
            connection_params["ssl"] = True
            connection_params["ssl_cert_reqs"] = ssl_context.verify_mode

        return connection_params

    @property
    def client(self) -> redis.Redis:
        """Get Redis client, reconnecting if necessary."""
        if self._client is None or self._connection_pool is None:
            try:
                connection_params = self._get_connection_params()
                self._connection_pool = redis.ConnectionPool(
                    **connection_params,
                    max_connections=settings.redis_connection_pool_size,
                )
                self._client = redis.Redis(
                    connection_pool=self._connection_pool,
                    socket_timeout=settings.redis_connection_timeout,
                    decode_responses=True,
                )
                self._client.ping()
                logger.info(
                    f"Reconnected to {settings.cache_provider.capitalize()} cache"
                )
            except RedisError as e:
                logger.error(
                    f"Failed to reconnect to {settings.cache_provider.capitalize()}: {str(e)}"
                )
                raise CacheConnectionError(
                    f"Failed to connect to {settings.cache_provider.capitalize()}: {str(e)}"
                )
        return self._client

    def get(self, key: str) -> Optional[str]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        Raises:
            CacheConnectionError: If cache connection fails
            CacheOperationError: If cache operation fails
        """
        try:
            return self.client.get(key)
        except RedisError as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to get from cache: {str(e)}")

    def set(self, key: str, value: str, ttl: int) -> None:
        """
        Set a value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Raises:
            CacheConnectionError: If cache connection fails
            CacheOperationError: If cache operation fails
        """
        try:
            self.client.setex(key, ttl, value)
        except RedisError as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to set in cache: {str(e)}")

    def get_json(self, key: str) -> Optional[Any]:
        """
        Get a JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value or None if not found

        Raises:
            CacheConnectionError: If cache connection fails
            CacheOperationError: If cache operation fails
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
            CacheConnectionError: If cache connection fails
            CacheOperationError: If cache operation fails
        """
        try:
            json_value = json.dumps(value)
            self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to encode value to JSON for key {key}: {str(e)}")
            raise CacheOperationError(f"Failed to encode to JSON: {str(e)}")


# Global singleton instance
redis_cache = CacheService()
