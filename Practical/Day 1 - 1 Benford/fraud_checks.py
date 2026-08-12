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

def benford_check(con, table_url):
    """Leading-digit distribution of amount_paid.

    Compare observed_pct against BENFORD_EXPECTED_PCT below - a large gap
    on any digit can indicate fabricated amounts.
    """
    
    result = con.sql(f"""
        WITH digits AS (
            SELECT LEFT(CAST(amount_paid AS VARCHAR), 1)::INT AS digit
            FROM '{table_url}' WHERE amount_paid >= 1
        ),
        
        # complete the SQL query
        
        
    """).df()
    
    result['expected_pct'] = result['digit'].map(BENFORD_EXPECTED_PCT)
    
    return result
    

# Azure blob container containing the data as parquet
TRANSACTIONS_TABLE ='https://tahastorage.blob.core.windows.net/training-public/transactions.parquet'
conn = duckdb.connect()

results = benford_check(conn,TRANSACTIONS_TABLE)

print(results)
