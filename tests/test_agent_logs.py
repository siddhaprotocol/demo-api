"""
Tests for the agent logs endpoint.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.constants.agent_logs_constants import CACHE_KEY_PREFIX
from app.main import app
from app.services.agent_logs_service import AgentLogsService

client = TestClient(app)


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_default_limit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with default limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint
    response = client.get("/logs/agent")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10  # Default limit is 10

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:10")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_custom_limit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with custom limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint with custom limit
    response = client.get("/logs/agent?limit=5")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:5")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_max_limit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with maximum limit."""
    # Mock Redis to return cache miss
    mock_get_json.return_value = None

    # Call the endpoint with max limit
    response = client.get("/logs/agent?limit=20")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:20")
    mock_set_json.assert_called_once()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_above_max_limit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with limit above maximum."""
    # Call the endpoint with limit above max
    response = client.get("/logs/agent?limit=21")

    # Should return a validation error
    assert response.status_code == 422
    data = response.json()
    assert "less than or equal to" in data["detail"][0]["msg"].lower()

    # Redis should not be accessed
    mock_get_json.assert_not_called()
    mock_set_json.assert_not_called()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_invalid_limit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with invalid limit."""
    # Call the endpoint with invalid limit
    response = client.get("/logs/agent?limit=0")

    # Should return a validation error
    assert response.status_code == 422
    data = response.json()
    assert "greater than or equal to" in data["detail"][0]["msg"].lower()

    # Redis should not be accessed
    mock_get_json.assert_not_called()
    mock_set_json.assert_not_called()


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_agent_logs_endpoint_cache_hit(mock_set_json, mock_get_json):
    """Test agent logs endpoint with cache hit."""
    # Create mock cached data
    cached_logs = ["Log message 1", "Log message 2", "Log message 3"]
    mock_get_json.return_value = cached_logs

    # Call the endpoint
    response = client.get("/logs/agent?limit=3")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data == cached_logs

    # Verify Redis interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:3")
    mock_set_json.assert_not_called()  # Should not set cache on hit


def test_deterministic_response():
    """Test that the endpoint returns deterministic responses across calls."""
    # Patch the system log generator to ensure deterministic results
    with patch(
        "app.services.agent_logs_service.AgentLogsService._generate_system_log",
        return_value="System log test",
    ):
        # Call the endpoint twice with the same limit
        with patch(
            "app.services.caching_service.redis_cache.get_json", return_value=None
        ):
            with patch("app.services.caching_service.redis_cache.set_json"):
                response1 = client.get("/logs/agent?limit=10")
                data1 = response1.json()

        with patch(
            "app.services.caching_service.redis_cache.get_json", return_value=None
        ):
            with patch("app.services.caching_service.redis_cache.set_json"):
                response2 = client.get("/logs/agent?limit=10")
                data2 = response2.json()

        # The two responses should be identical due to the fixed seed
        assert data1 == data2
        assert len(data1) == 10
