"""
Tests for the TreasuryService.
"""

from unittest.mock import patch

import pytest

from app.schemas.treasury_schemas import TreasuryMetrics
from app.services.treasury_service import (
    TREASURY_METRICS_CACHE_KEY,
    TREASURY_METRICS_CACHE_TTL,
    TreasuryService,
)


@pytest.fixture
def treasury_service():
    """TreasuryService fixture."""
    return TreasuryService


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_treasury_metrics_cache_miss(
    mock_set_json, mock_get_json, treasury_service
):
    """Test get_treasury_metrics with cache miss."""
    # Setup cache miss
    mock_get_json.return_value = None

    # Call the method
    result = treasury_service.get_treasury_metrics()

    # Verify result has expected constants
    assert isinstance(result, TreasuryMetrics)
    assert result.tvl == 1480000
    assert result.apy == 9.2

    # Verify cache interactions
    mock_get_json.assert_called_once_with(TREASURY_METRICS_CACHE_KEY)
    mock_set_json.assert_called_once()
    # Verify the first arg is the cache key
    assert mock_set_json.call_args[0][0] == TREASURY_METRICS_CACHE_KEY
    # Verify the third arg is the cache TTL
    assert mock_set_json.call_args[0][2] == TREASURY_METRICS_CACHE_TTL
    # Verify the second arg is the metrics dict
    metrics_dict = mock_set_json.call_args[0][1]
    assert metrics_dict["tvl"] == 1480000
    assert metrics_dict["apy"] == 9.2


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_treasury_metrics_cache_hit(mock_set_json, mock_get_json, treasury_service):
    """Test get_treasury_metrics with cache hit."""
    # Setup cache hit with cached values
    cached_data = {"tvl": 2000000, "apy": 8.5}
    mock_get_json.return_value = cached_data

    # Call the method
    result = treasury_service.get_treasury_metrics()

    # Verify result matches cached data
    assert isinstance(result, TreasuryMetrics)
    assert result.tvl == 2000000
    assert result.apy == 8.5

    # Verify cache interactions
    mock_get_json.assert_called_once_with(TREASURY_METRICS_CACHE_KEY)
    mock_set_json.assert_not_called()  # Should not set cache on hit
