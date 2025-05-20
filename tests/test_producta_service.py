"""
Tests for the ProductaService.
"""

from unittest.mock import patch

import pytest

from app.schemas.producta_schemas import ProductaStatus
from app.services.producta_service import ProductaService


@pytest.fixture
def producta_service():
    """ProductaService fixture."""
    return ProductaService


@patch("app.services.caching_service.redis_cache.get")
@patch("app.services.caching_service.redis_cache.set")
def test_get_status_cache_miss(mock_set, mock_get, producta_service):
    """Test get_status with cache miss."""
    # Setup cache miss
    mock_get.return_value = None

    # Call the method
    result = producta_service.get_status()

    # Verify result is a ProductaStatus with default "processing" status
    assert isinstance(result, ProductaStatus)
    assert result.status == "processing"

    # Verify cache interactions
    mock_get.assert_called_once_with(producta_service._cache_key)
    mock_set.assert_called_once_with(
        producta_service._cache_key, "processing", producta_service._cache_ttl
    )


@patch("app.services.caching_service.redis_cache.get")
@patch("app.services.caching_service.redis_cache.set")
def test_get_status_cache_hit(mock_set, mock_get, producta_service):
    """Test get_status with cache hit."""
    # Setup cache hit with string value
    mock_get.return_value = "done"

    # Call the method
    result = producta_service.get_status()

    # Verify result
    assert isinstance(result, ProductaStatus)
    assert result.status == "done"

    # Verify cache interactions
    mock_get.assert_called_once_with(producta_service._cache_key)
    mock_set.assert_not_called()  # Should not set cache on hit


@patch("app.services.caching_service.redis_cache.get")
@patch("app.services.caching_service.redis_cache.set")
def test_get_status_bytes_value(mock_set, mock_get, producta_service):
    """Test get_status with bytes value from Redis."""
    # Setup cache hit with bytes value (simulating Redis response)
    mock_get.return_value = b"done"

    # Call the method
    result = producta_service.get_status()

    # Verify result has been properly decoded
    assert isinstance(result, ProductaStatus)
    assert result.status == "done"

    # Verify cache interactions
    mock_get.assert_called_once_with(producta_service._cache_key)
    mock_set.assert_not_called()


@patch("app.services.caching_service.redis_cache.set")
def test_update_status(mock_set, producta_service):
    """Test update_status method."""
    # Create status update
    status_update = ProductaStatus(status="done")

    # Call the method
    result = producta_service.update_status(status_update)

    # Verify result
    assert isinstance(result, ProductaStatus)
    assert result.status == "done"

    # Verify cache interactions
    mock_set.assert_called_once_with(
        producta_service._cache_key, "done", producta_service._cache_ttl
    )


def test_status_validation():
    """Test that ProductaStatus validates status values."""
    # Valid statuses should not raise exceptions
    ProductaStatus(status="done")
    ProductaStatus(status="processing")

    # Invalid status should raise ValidationError
    with pytest.raises(ValueError):
        ProductaStatus(status="invalid")