"""
Cache-related error classes.
"""

from fastapi import HTTPException


class CacheConnectionError(HTTPException):
    """Raised when there is an error connecting to the cache server."""

    def __init__(self, detail: str = "Error connecting to cache server"):
        super().__init__(status_code=500, detail=detail)


class CacheOperationError(HTTPException):
    """Raised when there is an error performing a cache operation."""

    def __init__(self, detail: str = "Error performing cache operation"):
        super().__init__(status_code=500, detail=detail)
