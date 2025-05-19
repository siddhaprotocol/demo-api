"""
Tests for the invoices endpoint.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.constants.invoice_constants import CACHE_KEY_PREFIX
from app.main import app
from app.services.invoice_service import InvoiceService

client = TestClient(app)


def test_get_abbreviated_name():
    """Test the abbreviation function."""
    assert InvoiceService.get_abbreviated_name("US Treasury") == "UT"
    assert InvoiceService.get_abbreviated_name("Apple") == "APPL"
    assert InvoiceService.get_abbreviated_name("Microsoft Corporation") == "MC"
    assert (
        InvoiceService.get_abbreviated_name("International Business Machines") == "IBM"
    )
    assert InvoiceService.get_abbreviated_name("A B C D E") == "ABCD"


def test_invoices_fields_format():
    """Test that generated invoices follow the correct format."""
    invoices = InvoiceService.generate_invoices(20)

    for invoice in invoices:
        # ID format: INV-XXX-YYY where XXX is a 3-digit number
        assert invoice.id.startswith("INV-")
        id_parts = invoice.id.split("-")
        assert len(id_parts) == 3
        assert id_parts[0] == "INV"
        assert 100 <= int(id_parts[1]) <= 999

        # Client must not be empty
        assert invoice.client

        # Amount range
        assert 25000 <= invoice.amount <= 250000

        # Risk range
        assert 0.005 <= invoice.risk <= 0.080

        # TokenId format: TIQ-XXXX where XXXX is a 4-digit number
        assert invoice.tokenId.startswith("TIQ-")
        token_parts = invoice.tokenId.split("-")
        assert len(token_parts) == 2
        assert token_parts[0] == "TIQ"
        assert 1000 <= int(token_parts[1]) <= 9999

        # Status must be one of the valid options
        assert invoice.status in ("new", "processing", "funded")


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_default_limit(mock_set_json, mock_get_json):
    """Test invoices endpoint with default limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint
    response = client.get("/invoices")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 50

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:50")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_custom_limit(mock_set_json, mock_get_json):
    """Test invoices endpoint with custom limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint with custom limit
    response = client.get("/invoices?limit=10")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:10")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_max_limit(mock_set_json, mock_get_json):
    """Test invoices endpoint with maximum limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint with max limit
    response = client.get("/invoices?limit=100")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:100")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_above_max_limit(mock_set_json, mock_get_json):
    """Test invoices endpoint with limit above maximum."""
    # Call the endpoint with limit above max
    response = client.get("/invoices?limit=101")

    # Should return a validation error
    assert response.status_code == 422
    data = response.json()
    assert "less than or equal to" in data["detail"][0]["msg"].lower()

    # Redis should not be accessed
    mock_get_json.assert_not_called()
    mock_set_json.assert_not_called()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_invalid_limit(mock_set_json, mock_get_json):
    """Test invoices endpoint with invalid limit."""
    # Call the endpoint with invalid limit
    response = client.get("/invoices?limit=0")

    # Should return a validation error
    assert response.status_code == 422
    data = response.json()
    assert "greater than or equal to" in data["detail"][0]["msg"].lower()

    # Redis should not be accessed
    mock_get_json.assert_not_called()
    mock_set_json.assert_not_called()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_invoices_endpoint_cache_hit(mock_set_json, mock_get_json):
    """Test invoices endpoint with cache hit."""
    # Create mock cached data
    cached_invoices = InvoiceService.generate_invoices(5)
    mock_get_json.return_value = [invoice.model_dump() for invoice in cached_invoices]

    # Call the endpoint
    response = client.get("/invoices?limit=5")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:5")
    mock_set_json.assert_not_called()  # Should not set cache on hit
