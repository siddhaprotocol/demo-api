"""
Invoice routes for the mock invoice feed.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/invoices", tags=["invoices"])
