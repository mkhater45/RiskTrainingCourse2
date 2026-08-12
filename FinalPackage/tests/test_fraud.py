import duckdb
import pytest

from risk_utils.fraud import flag_velocity, benford_check


@pytest.fixture
def con():
    con = duckdb.connect()
    con.sql("""
        CREATE TABLE transactions AS
        SELECT * FROM (VALUES
            ('A1', 4500),
            ('A2', 18000),
            ('A2', 9200),
            ('A2', 7600),
            ('A3', 250)
        ) AS t(Account, Amount_Paid)
    """)
    return con


def test_flag_velocity_flags_high_count_accounts(con):
    result = flag_velocity(con, max_count=2)
    assert list(result["Account"]) == ["A2"]
    assert int(result["txn_count"].iloc[0]) == 3


def test_flag_velocity_empty_when_threshold_high(con):
    result = flag_velocity(con, max_count=10)
    assert len(result) == 0


def test_benford_check_returns_all_digits_present(con):
    result = benford_check(con)
    digits = set(result["digit"])
    assert digits == {4, 1, 9, 7, 2}  # leading digits of the fixture amounts
    assert abs(result["observed_pct"].sum() - 100.0) < 0.1


def test_benford_check_excludes_amounts_under_one():
    # regression test: amounts below $1 (e.g. 0.75) cast to text as "0.75",
    # and a naive LEFT(...,1) would read a leading digit of "0" - not a
    # real Benford digit. Those rows must be excluded, not counted.
    con = duckdb.connect()
    con.sql("""
        CREATE TABLE transactions AS
        SELECT * FROM (VALUES
            ('A1', 0.75),
            ('A1', 0.20),
            ('A2', 4500),
            ('A3', 4800)
        ) AS t(Account, Amount_Paid)
    """)
    result = benford_check(con)
    assert 0 not in set(result["digit"])
    assert int(result[result["digit"] == 4]["n"].iloc[0]) == 2
