"""Defensive checks that run before any risk logic touches the data.

These checks are designed to fail loudly instead of allowing models to run silently on bad input.
"""


def check_positive_amount(amount):
    """Raise if amount is not a positive number."""
    if amount <= 0:
        raise ValueError(f"amount_paid must be positive, got {amount}")
    return True


def check_required_fields(txn, required=("Account", "Amount_Paid", "Timestamp")):
    """Raise if txn is missing any required field."""
    missing = [f for f in required if txn.get(f) is None]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True

def validate_transaction(txn):
    """Run every check on a single transaction. Raises on first failure."""
    check_positive_amount(txn["Amount_Paid"])
    check_required_fields(txn)
    return True
    
def zscore_tag(amounts, threshold=3):
    """Flag statistically anomalous amounts using a simple Z-score.

    Uses population standard deviation, so the maximum possible score for
    n amounts is bounded by sqrt(n - 1) - with fewer than ~10 amounts, no
    outlier can ever clear the default threshold of 3, no matter how
    extreme it is. Fine for a batch of a few hundred transactions; not
    reliable on a handful of rows.
    """
    n = len(amounts)
    if n == 0:
        return []
    mean = sum(amounts) / n
    variance = sum((a - mean) ** 2 for a in amounts) / n
    std = variance ** 0.5
    if std == 0:
        return [False] * n
    return [abs(a - mean) / std > threshold for a in amounts]

