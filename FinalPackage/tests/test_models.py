import pytest

from risk_utils.models import CurrencyConverter, Transaction, BitcoinTransaction


# --- CurrencyConverter ---

def test_currency_converter_converts_known_currency():
    conv = CurrencyConverter()
    assert conv.toUSD(100, "Euro") == pytest.approx(108.0)


def test_currency_converter_raises_on_unknown_currency():
    conv = CurrencyConverter()
    with pytest.raises(ValueError):
        conv.toUSD(100, "Dogecoin")


# --- Transaction ---

def test_transaction_stores_fields():
    txn = Transaction("A1", "Alice", 250, "US Dollar", is_laundering=0)
    assert txn.account_number == "A1"
    assert txn.account_name == "Alice"
    assert txn.amount == 250
    assert txn.currency == "US Dollar"
    assert txn.is_laundering is False


def test_transaction_defaults_timestamp_when_not_given():
    txn = Transaction("A1", "Alice", 250, "US Dollar", is_laundering=0)
    assert txn.timestamp is not None


def test_transaction_keeps_given_timestamp():
    txn = Transaction("A1", "Alice", 250, "US Dollar", 0, timestamp="2024-01-01")
    assert txn.timestamp == "2024-01-01"


def test_transaction_is_large_true_above_10000_usd():
    txn = Transaction("A1", "Alice", 15000, "US Dollar", is_laundering=0)
    assert txn.is_large() is True


def test_transaction_is_large_false_below_10000_usd():
    txn = Transaction("A1", "Alice", 5000, "US Dollar", is_laundering=0)
    assert txn.is_large() is False


def test_transaction_is_large_converts_currency_before_comparing():
    # 9000 Euro * 1.08 = 9720 USD -> not large; but the raw amount alone is close to 10000
    txn = Transaction("A1", "Alice", 9000, "Euro", is_laundering=0)
    assert txn.is_large() is False
    txn2 = Transaction("A1", "Alice", 9500, "Euro", is_laundering=0)
    assert txn2.is_large() is True  # 9500 * 1.08 = 10260 USD


def test_transaction_is_reportable_requires_large_and_laundering():
    assert Transaction("A1", "Alice", 15000, "US Dollar", is_laundering=1).is_reportable() is True
    assert Transaction("A1", "Alice", 15000, "US Dollar", is_laundering=0).is_reportable() is False
    assert Transaction("A1", "Alice", 500, "US Dollar", is_laundering=1).is_reportable() is False


def test_transaction_summary_includes_account_and_flag():
    txn = Transaction("A1", "Alice", 250, "US Dollar", is_laundering=1)
    summary = txn.summary()
    assert "A1" in summary
    assert "LAUNDERING" in summary
    assert "250" in summary


# --- BitcoinTransaction ---

def test_bitcoin_transaction_requires_bitcoin_currency():
    with pytest.raises(ValueError):
        BitcoinTransaction("A1", "Alice", 1, "US Dollar", is_laundering=0)


def test_bitcoin_transaction_accepts_bitcoin_case_insensitive():
    txn = BitcoinTransaction("A1", "Alice", 1, "BITCOIN", is_laundering=0)
    assert txn.currency == "BITCOIN"


def test_bitcoin_transaction_is_always_reportable():
    small = BitcoinTransaction("A1", "Alice", 0.001, "Bitcoin", is_laundering=0)
    assert small.is_reportable() is True


def test_bitcoin_transaction_keeps_given_timestamp():
    # regression test: BitcoinTransaction.__init__ must forward the caller's
    # timestamp to Transaction.__init__ instead of discarding it
    txn = BitcoinTransaction("A1", "Alice", 1, "Bitcoin", 0, timestamp="2024-01-01")
    assert txn.timestamp == "2024-01-01"


def test_bitcoin_transaction_inherits_account_fields():
    txn = BitcoinTransaction("A1", "Alice", 2, "Bitcoin", is_laundering=1)
    assert txn.account_number == "A1"
    assert txn.account_name == "Alice"
    assert txn.is_laundering is True
