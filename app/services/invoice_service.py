"""
Invoice generation service.
"""

import random
from typing import List

from faker import Faker

from app.constants.invoice_constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_SECONDS,
    MAX_AMOUNT,
    MAX_RISK,
    MIN_AMOUNT,
    MIN_RISK,
    STATUS_WEIGHTS,
)
from app.core.logging import get_logger
from app.schemas.invoice_schemas import Invoice
from app.services.caching_service import redis_cache

logger = get_logger(__name__)

# Initialize Faker with fixed seed
fake = Faker()
Faker.seed(1234)  # Set random seed for Faker
random.seed(1234)  # Set random seed for reproducibility


class InvoiceService:
    """
    Service for generating and retrieving mock invoices.
    """

    @staticmethod
    def get_abbreviated_name(company_name: str) -> str:
        """
        Generate an abbreviated name from company name.

        Args:
            company_name: Company name to abbreviate

        Returns:
            Abbreviated company name
        """
        words = company_name.split()
        if len(words) == 1:
            return words[0][:4].upper()
        else:
            return "".join(word[0] for word in words[:4]).upper()

    @staticmethod
    def get_status_weighted() -> str:
        """
        Return a status based on weighted probabilities.

        Returns:
            Random status (new, processing, or funded)
        """
        return random.choices(
            list(STATUS_WEIGHTS.keys()),
            weights=list(STATUS_WEIGHTS.values()),
            k=1,
        )[0]

    @classmethod
    def generate_invoices(cls, limit: int) -> List[Invoice]:
        """
        Generate a list of mock invoices.

        Args:
            limit: Number of invoices to generate

        Returns:
            List of Invoice objects
        """
        invoices = []

        for _ in range(limit):
            client_name = fake.company()
            abbreviated = cls.get_abbreviated_name(client_name)

            invoices.append(
                Invoice(
                    id=f"INV-{random.randint(100, 999)}-{abbreviated}",
                    client=client_name,
                    amount=random.randint(MIN_AMOUNT, MAX_AMOUNT),
                    risk=round(random.uniform(MIN_RISK, MAX_RISK), 4),
                    tokenId=f"TIQ-{random.randint(1000, 9999)}",
                    status=cls.get_status_weighted(),
                )
            )

        return invoices

    @classmethod
    def get_invoices(cls, limit: int) -> List[Invoice]:
        """
        Get invoices with caching.

        Args:
            limit: Number of invoices to retrieve

        Returns:
            List of Invoice objects
        """
        # Check cache first
        cache_key = f"{CACHE_KEY_PREFIX}:{limit}"
        cached_data = redis_cache.get_json(cache_key)

        if cached_data:
            logger.debug(f"Cache hit for {cache_key}")
            return [Invoice(**item) for item in cached_data]

        # Generate new data
        logger.debug(f"Cache miss for {cache_key}, generating invoices")
        invoices = cls.generate_invoices(limit)

        # Cache the result
        redis_cache.set_json(
            cache_key,
            [invoice.model_dump() for invoice in invoices],
            CACHE_TTL_SECONDS,
        )

        return invoices
