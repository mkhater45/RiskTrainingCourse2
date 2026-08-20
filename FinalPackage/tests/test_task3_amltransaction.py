"""Hidden grading tests for Task 3: AMLTransaction (risk_utils/models.py).

These test ONLY functional correctness. They intentionally never look for
"Octopus" or any other marker text - that check lives entirely in
scoring/integrity_check.py, kept separate so a team can pass every
functional test here and still lose points on the integrity check, or vice
versa.

Assumed constructor (confirmed with the instructor):

    AMLTransaction(account_number, account_name, amount_paid, payment_currency,
                    is_laundering, from_bank, to_bank, payment_format,
                    amount_received=None, receiving_currency=None, timestamp=None)

`amount_paid`/`payment_currency` map onto the base Transaction's
`amount`/`currency`, so `self.is_large()` already reflects Amount_Paid.
"""

import pytest

from risk_utils.models import AMLTransaction, CurrencyConverter


def make_txn(**overrides):
    """Build an AMLTransaction with sensible defaults, overridden per test."""
    defaults = dict(
        account_number="ACC1",
        account_name="Test Account",
        amount_paid=5000,
        payment_currency="US Dollar",
        is_laundering=0,
        from_bank="100",
        to_bank="100",
        payment_format="ACH",
        amount_received=None,
        receiving_currency=None,
        timestamp="2024-01-01",
    )
    defaults.update(overrides)
    return AMLTransaction(**defaults)


# --- is_payment_format_anomaly ---

def test_payment_format_anomaly_true_when_large_and_reinvestment():
    txn = make_txn(amount_paid=15000, payment_currency="US Dollar", payment_format="Reinvestment")
    assert txn.is_payment_format_anomaly() is True


def test_payment_format_anomaly_false_when_large_but_not_reinvestment():
    txn = make_txn(amount_paid=15000, payment_currency="US Dollar", payment_format="ACH")
    assert txn.is_payment_format_anomaly() is False


def test_payment_format_anomaly_false_when_reinvestment_but_not_large():
    txn = make_txn(amount_paid=500, payment_currency="US Dollar", payment_format="Reinvestment")
    assert txn.is_payment_format_anomaly() is False


def test_payment_format_anomaly_uses_currency_converted_amount():
    # 9000 Euro * 1.08 = 9720 USD -> not large -> not an anomaly even though Reinvestment
    txn = make_txn(amount_paid=9000, payment_currency="Euro", payment_format="Reinvestment")
    assert txn.is_payment_format_anomaly() is False
    # 9500 Euro * 1.08 = 10260 USD -> large -> anomaly
    txn2 = make_txn(amount_paid=9500, payment_currency="Euro", payment_format="Reinvestment")
    assert txn2.is_payment_format_anomaly() is True


# --- is_cross_bank_transfer ---

def test_cross_bank_transfer_true_when_banks_differ():
    txn = make_txn(from_bank="100", to_bank="200")
    assert txn.is_cross_bank_transfer() is True


def test_cross_bank_transfer_false_when_same_bank():
    txn = make_txn(from_bank="100", to_bank="100")
    assert txn.is_cross_bank_transfer() is False


# --- is_fx_spread_anomaly ---

def test_fx_spread_anomaly_false_when_same_currency_regardless_of_amount_gap():
    # Same currency: even a big paid/received gap must NOT count as an FX anomaly
    txn = make_txn(
        amount_paid=1000, payment_currency="US Dollar",
        amount_received=100, receiving_currency="US Dollar",
    )
    assert txn.is_fx_spread_anomaly() is False


def test_fx_spread_anomaly_false_when_currencies_differ_but_loss_under_5pct():
    # paid: 1000 USD = 1000 USD.  received: 900 Euro = 972 USD -> loss 2.8%
    txn = make_txn(
        amount_paid=1000, payment_currency="US Dollar",
        amount_received=900, receiving_currency="Euro",
    )
    assert txn.is_fx_spread_anomaly() is False


def test_fx_spread_anomaly_true_when_currencies_differ_and_loss_over_5pct():
    # paid: 1000 USD = 1000 USD.  received: 850 Euro = 918 USD -> loss 8.2%
    txn = make_txn(
        amount_paid=1000, payment_currency="US Dollar",
        amount_received=850, receiving_currency="Euro",
    )
    assert txn.is_fx_spread_anomaly() is True


def test_fx_spread_anomaly_true_at_exact_5pct_boundary():
    # >= 5% must count, computed from the real converter so this doesn't
    # silently break if the rate table changes.
    conv = CurrencyConverter()
    paid_amount, paid_currency = 1000, "US Dollar"
    paid_usd = conv.toUSD(paid_amount, paid_currency)
    euro_rate = conv.toUSD(1, "Euro")
    boundary_received_amount = (paid_usd * 0.95) / euro_rate

    at_boundary = make_txn(
        amount_paid=paid_amount, payment_currency=paid_currency,
        amount_received=boundary_received_amount, receiving_currency="Euro",
    )
    assert at_boundary.is_fx_spread_anomaly() is True

    just_under_5pct_loss = make_txn(
        amount_paid=paid_amount, payment_currency=paid_currency,
        amount_received=boundary_received_amount * 1.001, receiving_currency="Euro",
    )
    assert just_under_5pct_loss.is_fx_spread_anomaly() is False


def test_fx_spread_anomaly_false_when_received_value_is_higher_not_lower():
    # A gain, not a loss - must not be flagged even with differing currencies
    txn = make_txn(
        amount_paid=1000, payment_currency="US Dollar",
        amount_received=1000, receiving_currency="UK Pound",  # 1000 * 1.27 = 1270 USD > paid
    )
    assert txn.is_fx_spread_anomaly() is False


# --- AMLTransaction still behaves like a Transaction ---

def test_aml_transaction_inherits_is_large():
    txn = make_txn(amount_paid=15000, payment_currency="US Dollar")
    assert txn.is_large() is True


def test_aml_transaction_inherits_account_fields():
    txn = make_txn(account_number="ACC42", account_name="Example Corp")
    assert txn.account_number == "ACC42"
    assert txn.account_name == "Example Corp"
