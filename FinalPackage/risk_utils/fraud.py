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
def flag_scatter_payments(con,max_recipients=5):
    return con.sql(f"""
            SELECT from_account, COUNT( distinct to_account) AS txn_count
            FROM transactions
            GROUP BY from_account
            HAVING COUNT( distinct to_account) > {max_recipients}
        """).df()

@timer
def flag_round_trips(con):
    return con.sql(f"""
                select t1.* from transactions t1
                inner join transactions t2
                where t1.from_account = t2.to_account and
                t1.to_account = t2.from_account
                where t1.timestamp < t2.timestamp
            """).df()

@timer
def flag_rapid_pass_through(con,threshold_ratio = 0.9):
    return con.sql(f"""
                    with out as (
                   select  from_account, from bank, sum(amount_paid) as total_out
                   from transactions group by from_account, from_bank),

                   in as ( select t.to_account, t.to_bank, sum(t.amount_received) as total_in
                   from transactions t inner join out o on t.to_account = o.from_account and t.to_bank = o.from_bank
                   group by t.to_account, t.to_bank)

                   select o.from_account as account_no, o.from_bank as bank,  o.total_out/i.total_in
                   from out o inner join in i on o.from_account = i.to_account and o.from_bank = i.to_bank
                   where o.total_out/i.total_in > {threshold_ratio} 

                   
                    
                   
                   
                   )




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