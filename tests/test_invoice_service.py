"""
Tests for the invoice service.
"""

from unittest.mock import patch

from app.constants.invoice_constants import CACHE_KEY_PREFIX, CACHE_TTL_SECONDS
from app.services.invoice_service import InvoiceService


def test_get_status_weighted():
    """Test the weighted status function."""
    # Test multiple calls to ensure the distribution is roughly as expected
    statuses = [InvoiceService.get_status_weighted() for _ in range(1000)]

    # Count occurrences
    new_count = statuses.count("new")
    processing_count = statuses.count("processing")
    funded_count = statuses.count("funded")

    # Verify distribution is roughly as expected (with some margin for randomness)
    assert 550 <= new_count <= 650  # ~60%
    assert 250 <= processing_count <= 350  # ~30%
    assert 80 <= funded_count <= 120  # ~10%


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_invoices_cache_miss(mock_set_json, mock_get_json):
    """Test get_invoices with cache miss."""
    # Setup cache miss
    mock_get_json.return_value = None

    # Call the method
    invoices = InvoiceService.get_invoices(5)

    # Verify results
    assert len(invoices) == 5

    # Verify cache interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:5")
    mock_set_json.assert_called_once()

    # Verify the right data was cached
    cache_key = mock_set_json.call_args[0][0]
    cache_data = mock_set_json.call_args[0][1]
    cache_ttl = mock_set_json.call_args[0][2]

    assert cache_key == f"{CACHE_KEY_PREFIX}:5"
    assert len(cache_data) == 5
    assert all(isinstance(item, dict) for item in cache_data)
    assert cache_ttl == CACHE_TTL_SECONDS


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_invoices_cache_hit(mock_set_json, mock_get_json):
    """Test get_invoices with cache hit."""
    # Generate some invoices to use as cached data
    generated_invoices = InvoiceService.generate_invoices(5)
    mock_get_json.return_value = [
        invoice.model_dump() for invoice in generated_invoices
    ]

    # Call the method
    invoices = InvoiceService.get_invoices(5)

    # Verify results
    assert len(invoices) == 5

    # Verify all invoices match the cached data
    for i, invoice in enumerate(invoices):
        assert invoice.id == generated_invoices[i].id
        assert invoice.client == generated_invoices[i].client
        assert invoice.amount == generated_invoices[i].amount
        assert invoice.risk == generated_invoices[i].risk
        assert invoice.tokenId == generated_invoices[i].tokenId
        assert invoice.status == generated_invoices[i].status

    # Verify cache interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:5")
    mock_set_json.assert_not_called()  # Should not set cache on hit
