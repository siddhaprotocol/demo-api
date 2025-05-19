"""
Constants related to the invoice feed.
"""

# Cache settings
CACHE_KEY_PREFIX = "demo:invoices"
CACHE_TTL_SECONDS = 60

# Data generation settings
RANDOM_SEED = 1234
INVOICE_ID_PREFIX = "INV"
TOKEN_ID_PREFIX = "TIQ"

# Amount range
MIN_AMOUNT = 25000
MAX_AMOUNT = 250000

# Risk range
MIN_RISK = 0.005
MAX_RISK = 0.080

# Invoice ID ranges
MIN_INVOICE_NUMBER = 100
MAX_INVOICE_NUMBER = 999

# Token ID ranges
MIN_TOKEN_NUMBER = 1000
MAX_TOKEN_NUMBER = 9999

# Status weights
STATUS_WEIGHTS = {
    "new": 0.6,
    "processing": 0.3,
    "funded": 0.1
}

# Query parameters
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
MIN_LIMIT = 1