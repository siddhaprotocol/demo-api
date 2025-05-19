"""
Constants related to the invoice feed.
"""

# Cache settings
CACHE_KEY_PREFIX = "demo:invoices"
CACHE_TTL_SECONDS = 60

# Amount range
MIN_AMOUNT = 25000
MAX_AMOUNT = 250000

# Risk range
MIN_RISK = 0.005
MAX_RISK = 0.080

# Status weights
STATUS_WEIGHTS = {"new": 0.6, "processing": 0.3, "funded": 0.1}

# Query parameters
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
MIN_LIMIT = 1
