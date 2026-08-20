"""Hidden grading tests for Task 4: fraud.py's three set-based SQL checks.

Functional correctness only - never asserts on a "dolphin" column. Tests
look up expected accounts/pairs by VALUE (searching across whatever columns
the team's query happens to produce), not by an assumed column name, except
where the task spec itself names the column (From_Account/To_Account are
explicit in the spec's join condition; the aggregate metric column's name is
never specified there, so we don't require a particular name for it).
"""

import duckdb
import pytest

from risk_utils.fraud import (
    flag_scatter_payments,
    flag_round_trips,
    flag_rapid_pass_through,
)

TXN_COLUMNS = (
    "Timestamp, From_Bank, From_Account, To_Bank, To_Account, "
    "Amount_Received, Receiving_Currency, Amount_Paid, Payment_Currency, "
    "Payment_Format, Is_Laundering"
)


def _row_present(df, **expected_cell_values):
    """True if some row in df matches ALL given column=value pairs.

    Only checks columns that exist in df, so it tolerates whatever extra
    columns (e.g. a required "dolphin" alias) a team's query adds.
    """
    mask = None
    for col, val in expected_cell_values.items():
        if col not in df.columns:
            return False
        col_mask = df[col] == val
        mask = col_mask if mask is None else (mask & col_mask)
    return bool(mask is not None and mask.any())


def _any_column_contains(df, value):
    """True if `value` appears anywhere in df, regardless of column name."""
    return any((df[c] == value).any() for c in df.columns)


# --- flag_scatter_payments ---

@pytest.fixture
def con_scatter():
    con = duckdb.connect()
    con.sql(f"""
        CREATE TABLE transactions AS
        SELECT * FROM (VALUES
            ('9/1/2022 1:00', '100', 'S1', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:01', '100', 'S1', '100', 'R2', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:02', '100', 'S1', '100', 'R3', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:03', '100', 'S1', '100', 'R4', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:04', '100', 'S1', '100', 'R5', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:05', '100', 'S2', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:06', '100', 'S2', '100', 'R2', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:07', '100', 'S2', '100', 'R3', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:08', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:09', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:10', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:11', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:12', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:13', '100', 'S3', '100', 'R1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0)
        ) AS t({TXN_COLUMNS})
    """)
    return con


def test_scatter_flags_account_with_5_or_more_unique_recipients(con_scatter):
    result = flag_scatter_payments(con_scatter, max_recipients=5)
    assert _row_present(result, From_Account="S1")


def test_scatter_does_not_flag_account_with_fewer_unique_recipients(con_scatter):
    result = flag_scatter_payments(con_scatter, max_recipients=5)
    assert not _row_present(result, From_Account="S2")


def test_scatter_counts_unique_recipients_not_transaction_count(con_scatter):
    # S3 sends 6 transactions but to the SAME single recipient - must not be flagged
    result = flag_scatter_payments(con_scatter, max_recipients=5)
    assert not _row_present(result, From_Account="S3")


def test_scatter_respects_max_recipients_threshold(con_scatter):
    # With a lower threshold, S2 (3 unique recipients) should now qualify
    result = flag_scatter_payments(con_scatter, max_recipients=3)
    assert _row_present(result, From_Account="S2")


# --- flag_round_trips ---

@pytest.fixture
def con_roundtrip():
    con = duckdb.connect()
    con.sql(f"""
        CREATE TABLE transactions AS
        SELECT * FROM (VALUES
            ('9/1/2022 1:00', '100', 'A', '100', 'B', 500.0, 'US Dollar', 500.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:05', '100', 'B', '100', 'A', 480.0, 'US Dollar', 480.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:10', '100', 'C', '100', 'D', 500.0, 'US Dollar', 500.0, 'US Dollar', 'ACH', 0)
        ) AS t({TXN_COLUMNS})
    """)
    return con


def test_round_trip_flags_mutual_pair(con_roundtrip):
    result = flag_round_trips(con_roundtrip)
    pair_found = _row_present(result, From_Account="A", To_Account="B") or \
        _row_present(result, From_Account="B", To_Account="A")
    assert pair_found


def test_round_trip_ignores_one_directional_transfer(con_roundtrip):
    result = flag_round_trips(con_roundtrip)
    assert not _any_column_contains(result, "C")
    assert not _any_column_contains(result, "D")


# --- flag_rapid_pass_through ---

@pytest.fixture
def con_passthrough():
    con = duckdb.connect()
    con.sql(f"""
        CREATE TABLE transactions AS
        SELECT * FROM (VALUES
            -- P1: inbound 1000, outbound 950 -> ratio 0.95, >= 0.9 threshold -> flagged
            ('9/1/2022 1:00', '100', 'X1', '100', 'P1', 1000.0, 'US Dollar', 1000.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:01', '100', 'P1', '100', 'Y1', 950.0, 'US Dollar', 950.0, 'US Dollar', 'ACH', 0),
            -- P2: inbound 1000, outbound 500 -> ratio 0.5, below threshold -> not flagged
            ('9/1/2022 1:02', '100', 'A2', '100', 'P2', 1000.0, 'US Dollar', 1000.0, 'US Dollar', 'ACH', 0),
            ('9/1/2022 1:03', '100', 'P2', '100', 'B2', 500.0, 'US Dollar', 500.0, 'US Dollar', 'ACH', 0),
            -- P3: outbound only, zero inbound -> must not crash the query (div-by-zero) and must not be flagged
            ('9/1/2022 1:04', '100', 'P3', '100', 'Z1', 100.0, 'US Dollar', 100.0, 'US Dollar', 'ACH', 0)
        ) AS t({TXN_COLUMNS})
    """)
    return con


def test_pass_through_flags_account_at_or_above_ratio(con_passthrough):
    result = flag_rapid_pass_through(con_passthrough, threshold_ratio=0.9)
    assert _any_column_contains(result, "P1")


def test_pass_through_does_not_flag_account_below_ratio(con_passthrough):
    result = flag_rapid_pass_through(con_passthrough, threshold_ratio=0.9)
    assert not _any_column_contains(result, "P2")


def test_pass_through_handles_zero_inbound_without_crashing(con_passthrough):
    # Should not raise (e.g. from a division by zero) and P3 should not be flagged
    result = flag_rapid_pass_through(con_passthrough, threshold_ratio=0.9)
    assert not _any_column_contains(result, "P3")


def test_pass_through_respects_custom_threshold(con_passthrough):
    # Lowering the bar to 0.4 should now catch P2 (ratio 0.5) too
    result = flag_rapid_pass_through(con_passthrough, threshold_ratio=0.4)
    assert _any_column_contains(result, "P2")
