import pytest

from risk_utils.validation import (
    check_positive_amount,
    check_required_fields,
    zscore_tag,
    validate_transaction,
)


def test_check_positive_amount_raises_on_negative():
    with pytest.raises(ValueError):
        check_positive_amount(-100)


def test_check_positive_amount_passes_on_positive():
    assert check_positive_amount(100) is True


def test_check_required_fields_raises_on_missing():
    with pytest.raises(ValueError):
        check_required_fields({"Account": "A1"})


def test_check_required_fields_passes_when_complete():
    txn = {"Account": "A1", "Amount_Paid": 100, "Timestamp": "2024-01-01"}
    assert check_required_fields(txn) is True


def test_zscore_tag_flags_outlier():
    # population-std z-scores are bounded by sqrt(n - 1), so this needs
    # enough points for the outlier to actually clear threshold=3
    amounts = [480, 500, 510, 495, 505, 520, 490, 515, 500, 480, 495, 50000]
    tags = zscore_tag(amounts)
    assert tags == [False] * 11 + [True]


def test_zscore_tag_returns_all_false_on_small_sample():
    # fewer than ~10 points can never clear threshold=3, by construction
    tags = zscore_tag([500, 480, 510, 495000, 520])
    assert tags == [False, False, False, False, False]


def test_validate_transaction():
    txn = {"Account": "A1", "Amount_Paid": 4500, "Timestamp": "2024-01-01"}
    assert validate_transaction(txn) is True


def test_validate_transaction_raises_on_negative_amount():
    txn = {"Account": "A1", "Amount_Paid": -50, "Timestamp": "2024-01-01"}
    with pytest.raises(ValueError):
        validate_transaction(txn)
