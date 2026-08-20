"""Fraud checks - stretch content from Day 3.

Both checks run as SQL directly against the DuckDB table `io.py` loaded,
rather than pulling every row back into Python first. `flag_velocity` and
`benford_check` reuse Day 1 SQL (GROUP BY / HAVING, CTEs) against a real
fraud-detection problem.
"""

from .decorators import timer

BENFORD_EXPECTED_PCT = {
    1: 30.1, 2: 17.6, 3: 12.5, 4: 9.7, 5: 7.9,
    6: 6.7, 7: 5.8, 8: 5.1, 9: 4.6,
}



def flag_velocity(con, max_count=5):
    """Accounts with more than max_count transactions in the table."""
    return con.sql(f"""
        SELECT account, COUNT(*) AS txn_count
        FROM transactions
        GROUP BY account
        HAVING COUNT(*) > {max_count}
    """).df()


@timer
def benford_check(con):
    """Leading-digit distribution of amount_paid.

    Compare observed_pct against BENFORD_EXPECTED_PCT below - a large gap
    on any digit can indicate fabricated amounts.
    """
    result = con.sql("""
        WITH digits AS (
            SELECT LEFT(CAST(amount_paid AS VARCHAR), 1)::INT AS digit
            FROM transactions WHERE amount_paid >= 1
        ),
        counts AS (SELECT digit, COUNT(*) AS n FROM digits GROUP BY digit),
        total  AS (SELECT SUM(n) AS total_n FROM counts)
        SELECT digit, n, ROUND(n * 100.0 / total_n, 1) AS observed_pct
        FROM counts, total
        ORDER BY digit
    """).df()
    result['expected_pct'] = result['digit'].map(BENFORD_EXPECTED_PCT)
    
    return result