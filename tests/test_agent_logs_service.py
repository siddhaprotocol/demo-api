"""
Tests for the agent logs service.
"""

from unittest.mock import patch

import pytest

from app.constants.agent_logs_constants import CACHE_KEY_PREFIX, CACHE_TTL_SECONDS
from app.services.agent_logs_service import AgentLogsService


def test_generate_logs_limit():
    """Test that generate_logs respects the limit."""
    # Generate logs with different limits
    logs_5 = AgentLogsService.generate_logs(5)
    logs_10 = AgentLogsService.generate_logs(10)
    logs_20 = AgentLogsService.generate_logs(20)

    # Verify the correct number of logs is generated
    assert len(logs_5) == 5
    assert len(logs_10) == 10
    assert len(logs_20) == 20

    # Verify logs are strings
    assert all(isinstance(log, str) for log in logs_5)
    assert all(isinstance(log, str) for log in logs_10)
    assert all(isinstance(log, str) for log in logs_20)


def test_generate_logs_deterministic():
    """Test that generate_logs produces deterministic results."""
    # Temporarily patch the system log generator to avoid timestamp variations
    with patch(
        "app.services.agent_logs_service.AgentLogsService._generate_system_log"
    ) as mock_system_log:
        mock_system_log.return_value = "System heartbeat test"

        # Generate logs twice with the same limit
        logs_first = AgentLogsService.generate_logs(10)
        logs_second = AgentLogsService.generate_logs(10)

        # The logs should be identical across calls due to the fixed seed
        assert logs_first == logs_second


def test_log_message_format():
    """Test that log messages follow the expected format patterns."""
    logs = AgentLogsService.generate_logs(
        50
    )  # Generate a large sample for better coverage

    # Check for presence of all log types
    invoice_logs = [log for log in logs if "invoice" in log.lower()]
    risk_logs = [log for log in logs if "risk" in log.lower()]
    funding_logs = [
        log for log in logs if "fund" in log.lower() or "batch" in log.lower()
    ]
    system_logs = [
        log for log in logs if "heartbeat" in log.lower() or "system" in log.lower()
    ]

    # Verify we have logs of each type
    assert len(invoice_logs) > 0
    assert len(risk_logs) > 0
    assert len(funding_logs) > 0
    assert len(system_logs) > 0

    # Verify the logs contain expected patterns for each type
    invoice_patterns = ["invoice #", "processed", "validation", "parser"]
    assert any(
        any(pattern in log.lower() for pattern in invoice_patterns)
        for log in invoice_logs
    )

    risk_patterns = ["risk", "score", "assessment", "threshold"]
    assert any(
        any(pattern in log.lower() for pattern in risk_patterns) for log in risk_logs
    )

    funding_patterns = ["fund", "batch", "sent", "lock-up", "$"]
    assert any(
        any(pattern in log.lower() for pattern in funding_patterns)
        for log in funding_logs
    )

    system_patterns = ["heartbeat", "processed", "health", "sync", "api"]
    assert any(
        any(pattern in log.lower() for pattern in system_patterns)
        for log in system_logs
    )


def test_invoice_log_generator():
    """Test the invoice log generator specifically."""
    # Generate 10 invoice logs
    logs = [AgentLogsService._generate_invoice_log() for _ in range(10)]

    # Verify all logs have expected format elements
    for log in logs:
        assert "#" in log  # Should have an invoice number

    # Sample different logs to ensure we get variation
    assert len(set(logs)) > 1


def test_risk_log_generator():
    """Test the risk log generator specifically."""
    # Generate 10 risk logs
    logs = [AgentLogsService._generate_risk_log() for _ in range(10)]

    # Verify all logs have expected format elements
    for log in logs:
        assert any(x in log for x in ["risk", "Risk"])

    # Sample different logs to ensure we get variation
    assert len(set(logs)) > 1


def test_funding_log_generator():
    """Test the funding log generator specifically."""
    # Generate 10 funding logs
    logs = [AgentLogsService._generate_funding_log() for _ in range(10)]

    # Verify all logs have expected format elements
    for log in logs:
        assert any(x in log for x in ["$", "Batch", "fund", "Fund"])

    # Sample different logs to ensure we get variation
    assert len(set(logs)) > 1


def test_system_log_generator():
    """Test the system log generator specifically."""
    # Generate 10 system logs
    logs = [AgentLogsService._generate_system_log() for _ in range(10)]

    # Verify all logs have expected format elements
    for log in logs:
        assert any(
            x in log
            for x in ["ms", "heartbeat", "Processed", "health", "Database", "API"]
        )

    # Sample different logs to ensure we get variation
    assert len(set(logs)) > 1


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_agent_logs_cache_miss(mock_set_json, mock_get_json):
    """Test get_agent_logs with cache miss."""
    # Setup cache miss
    mock_get_json.return_value = None

    # Call the method
    logs = AgentLogsService.get_agent_logs(5)

    # Verify results
    assert len(logs) == 5
    assert all(isinstance(log, str) for log in logs)

    # Verify cache interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:5")
    mock_set_json.assert_called_once()

    # Verify the right data was cached
    cache_key = mock_set_json.call_args[0][0]
    cache_data = mock_set_json.call_args[0][1]
    cache_ttl = mock_set_json.call_args[0][2]

    assert cache_key == f"{CACHE_KEY_PREFIX}:5"
    assert len(cache_data) == 5
    assert all(isinstance(log, str) for log in cache_data)
    assert cache_ttl == CACHE_TTL_SECONDS


@patch("app.services.caching_service.redis_cache.get_json")
@patch("app.services.caching_service.redis_cache.set_json")
def test_get_agent_logs_cache_hit(mock_set_json, mock_get_json):
    """Test get_agent_logs with cache hit."""
    # Setup cache hit with cached values
    cached_data = ["Log message 1", "Log message 2", "Log message 3"]
    mock_get_json.return_value = cached_data

    # Call the method
    logs = AgentLogsService.get_agent_logs(3)

    # Verify results match cached data
    assert logs == cached_data
    assert len(logs) == 3

    # Verify cache interactions
    mock_get_json.assert_called_once_with(f"{CACHE_KEY_PREFIX}:3")
    mock_set_json.assert_not_called()  # Should not set cache on hit


def test_generate_logs_max_limit():
    """Test that generate_logs respects the maximum limit."""
    # Generate logs with a limit above the maximum
    logs = AgentLogsService.generate_logs(30)  # MAX_LIMIT is 20

    # Should be capped at the maximum limit
    assert len(logs) == 20
