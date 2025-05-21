"""
Agent logs service for retrieving agent activity data.
"""

import datetime
import random
from datetime import UTC
from typing import List

from faker import Faker

from app.constants.agent_logs_constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_SECONDS,
    MAX_LIMIT,
)
from app.core.logging import get_logger
from app.services.caching_service import redis_cache

logger = get_logger(__name__)

# Initialize Faker with fixed seed as specified in requirements
random.seed(4321)  # Set random seed for reproducibility first
fake = Faker()
Faker.seed(4321)  # Set random seed for Faker

# Pre-defined message templates for realistic agent logs
INVOICE_LOG_TEMPLATES = [
    "Parser finished invoice #{invoice_id}",
    "Processing invoice #{invoice_id} from {company}",
    "Invoice #{invoice_id} validation complete",
    "Invoice #{invoice_id} added to batch #{batch_id}",
    "Verified invoice #{invoice_id} signatures",
]

RISK_LOG_TEMPLATES = [
    "RiskScore updated → {risk_score}",
    "Risk assessment for invoice #{invoice_id} completed: {risk_score}",
    "Completed risk assessment for batch #{batch_id}",
    "Updated risk model with {count} new datapoints",
    "Risk threshold adjusted to {risk_score}",
]

FUNDING_LOG_TEMPLATES = [
    "Batch {batch_id} sent for funding",
    "Funded invoice #{invoice_id} for ${amount}",
    "Liquidity check complete: ${amount} available",
    "Funds lock-up updated to ${amount}",
    "Funding rate adjusted to {rate}%",
]

SYSTEM_LOG_TEMPLATES = [
    "Matching engine heartbeat {timestamp}",
    "Processed {count} transactions in {time}ms",
    "System health check: {status}",
    "Database sync completed in {time}ms",
    "API response time: {time}ms (p95)",
]


class AgentLogsService:
    """Service for generating and retrieving agent logs."""

    @classmethod
    def _reset_random_state(cls) -> None:
        """Reset random state to ensure deterministic results."""
        random.seed(4321)
        Faker.seed(4321)

    @classmethod
    def _generate_invoice_log(cls) -> str:
        """Generate a random invoice-related log message."""
        template = random.choice(INVOICE_LOG_TEMPLATES)
        return template.format(
            invoice_id=random.randint(1000, 9999),
            company=fake.company(),
            batch_id=random.randint(1, 100),
        )

    @classmethod
    def _generate_risk_log(cls) -> str:
        """Generate a random risk-related log message."""
        template = random.choice(RISK_LOG_TEMPLATES)
        return template.format(
            risk_score=round(random.uniform(0.01, 0.99), 2),
            invoice_id=random.randint(1000, 9999),
            batch_id=random.randint(1, 100),
            count=random.randint(10, 500),
        )

    @classmethod
    def _generate_funding_log(cls) -> str:
        """Generate a random funding-related log message."""
        template = random.choice(FUNDING_LOG_TEMPLATES)
        return template.format(
            batch_id=random.randint(1, 100),
            invoice_id=random.randint(1000, 9999),
            amount=f"{random.randint(100_000, 10_000_000):,}",
            rate=round(random.uniform(1.0, 15.0), 1),
        )

    @classmethod
    def _generate_system_log(cls) -> str:
        """Generate a random system-related log message."""
        template = random.choice(SYSTEM_LOG_TEMPLATES)
        now = datetime.datetime.now(UTC)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        return template.format(
            timestamp=timestamp,
            count=random.randint(100, 10000),
            time=random.randint(5, 200),
            status=random.choice(["green", "yellow"]),
        )

    @classmethod
    def generate_logs(cls, limit: int) -> List[str]:
        """
        Generate a list of deterministic agent logs.

        Args:
            limit: Number of log messages to generate

        Returns:
            List of agent log messages
        """
        # Reset random state to ensure deterministic results
        cls._reset_random_state()

        # Ensure limit is within bounds
        limit = min(limit, MAX_LIMIT)

        log_generators = [
            cls._generate_invoice_log,
            cls._generate_risk_log,
            cls._generate_funding_log,
            cls._generate_system_log,
        ]

        logs = []
        for _ in range(limit):
            # Select a random generator with equal probability
            generator = random.choice(log_generators)
            logs.append(generator())

        return logs

    @classmethod
    def get_agent_logs(cls, limit: int) -> List[str]:
        """
        Get agent logs with caching.

        Args:
            limit: Number of log messages to retrieve

        Returns:
            List of agent log message strings
        """
        # Check cache first
        cache_key = f"{CACHE_KEY_PREFIX}:{limit}"
        cached_data = redis_cache.get_json(cache_key)

        if cached_data:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_data

        # Generate new data
        logger.debug(f"Cache miss for {cache_key}, generating agent logs")
        logs = cls.generate_logs(limit)

        # Cache the result
        redis_cache.set_json(cache_key, logs, CACHE_TTL_SECONDS)

        return logs
