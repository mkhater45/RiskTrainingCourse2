import duckdb


BENFORD_EXPECTED_PCT = {
    1: 30.1, 
    2: 17.6, 
    3: 12.5, 
    4: 9.7, 
    5: 7.9,
    6: 6.7, 
    7: 5.8, 
    8: 5.1, 
    9: 4.6,
}

def benford_check(con):
    """Leading-digit distribution of amount_paid.

    Compare observed_pct against BENFORD_EXPECTED_PCT below - a large gap
    on any digit can indicate fabricated amounts.
    """
    
    result = con.sql(f"""
        WITH digits AS (
            SELECT LEFT(CAST(amount_paid AS VARCHAR), 1)::INT AS digit
            FROM transactions WHERE amount_paid >= 1
        )
        
        -- complete the SQL query
        select * from digits limit 10
        
    """).df()
    
    result['expected_pct'] = result['digit'].map(BENFORD_EXPECTED_PCT)
    
    return result
    

# Local DuckDB file containing the transactions table
conn = duckdb.connect("..//..//risk.duckdb")

results = benford_check(conn)

conn.close()

print(results)


