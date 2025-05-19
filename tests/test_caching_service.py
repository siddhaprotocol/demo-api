"""
Tests for the Redis caching service.
"""

import json
from unittest.mock import Mock, patch

import pytest
import redis

from app.errors.cache_errors import CacheOperationError
from app.services.caching_service import RedisCacheService


@pytest.fixture
def mock_redis_client():
    """Mock Redis client fixture."""
    with patch("redis.Redis") as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def cache_service(mock_redis_client):
    """Cache service fixture with mocked Redis client."""
    service = RedisCacheService()
    service._client = mock_redis_client
    return service


def test_singleton_pattern():
    """Test that RedisCacheService is a singleton."""
    service1 = RedisCacheService()
    service2 = RedisCacheService()
    assert service1 is service2


def test_get_success(cache_service, mock_redis_client):
    """Test successful get operation."""
    mock_redis_client.get.return_value = "test_value"
    result = cache_service.get("test_key")

    assert result == "test_value"
    mock_redis_client.get.assert_called_once_with("test_key")


def test_get_failure(cache_service, mock_redis_client):
    """Test get operation failure."""
    mock_redis_client.get.side_effect = redis.RedisError("Connection error")

    with pytest.raises(CacheOperationError):
        cache_service.get("test_key")


def test_set_success(cache_service, mock_redis_client):
    """Test successful set operation."""
    cache_service.set("test_key", "test_value", 60)

    mock_redis_client.setex.assert_called_once_with("test_key", 60, "test_value")


def test_set_failure(cache_service, mock_redis_client):
    """Test set operation failure."""
    mock_redis_client.setex.side_effect = redis.RedisError("Connection error")

    with pytest.raises(CacheOperationError):
        cache_service.set("test_key", "test_value", 60)


def test_get_json_success(cache_service, mock_redis_client):
    """Test successful get_json operation."""
    test_data = {"key": "value"}
    mock_redis_client.get.return_value = json.dumps(test_data)

    result = cache_service.get_json("test_key")

    assert result == test_data
    mock_redis_client.get.assert_called_once_with("test_key")


def test_get_json_not_found(cache_service, mock_redis_client):
    """Test get_json when key not found."""
    mock_redis_client.get.return_value = None

    result = cache_service.get_json("test_key")

    assert result is None
    mock_redis_client.get.assert_called_once_with("test_key")


def test_get_json_invalid_json(cache_service, mock_redis_client):
    """Test get_json with invalid JSON."""
    mock_redis_client.get.return_value = "invalid json"

    result = cache_service.get_json("test_key")

    assert result is None
    mock_redis_client.get.assert_called_once_with("test_key")


def test_set_json_success(cache_service, mock_redis_client):
    """Test successful set_json operation."""
    test_data = {"key": "value"}

    cache_service.set_json("test_key", test_data, 60)

    mock_redis_client.setex.assert_called_once_with(
        "test_key", 60, json.dumps(test_data)
    )


def test_set_json_failure(cache_service, mock_redis_client):
    """Test set_json operation failure."""
    test_data = {"key": "value"}
    mock_redis_client.setex.side_effect = redis.RedisError("Connection error")

    with pytest.raises(CacheOperationError):
        cache_service.set_json("test_key", test_data, 60)


def test_set_json_nonserializable(cache_service):
    """Test set_json with non-serializable data."""
    # Create a circular reference that can't be serialized
    test_data = {}
    test_data["self"] = test_data

    with pytest.raises(CacheOperationError):
        cache_service.set_json("test_key", test_data, 60)
