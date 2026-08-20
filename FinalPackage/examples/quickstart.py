"""End-to-end demo of risk_utils, tying every module from Day 2 and
Day 3 together against the sample data in data/.

Run from the project root:

    pip install -e .
    python examples/quickstart.py
"""

from risk_utils import (
    Transaction,
    BitcoinTransaction,
    validate_transaction,
    load_folder,
    flag_velocity,
    benford_check,
)

# 1. Load every CSV/Excel file in data/ into a local DuckDB database
con = load_folder("data")
print("--- transactions table ---")
print(con.sql("SELECT COUNT(*) AS n FROM transactions").df())

# 2. Validate a transaction before scoring it
txn = {"Account": "A2", "Amount_Paid": 18000, "Timestamp": "2024-01-05"}
validate_transaction(txn)

# 3. Score it with the Transaction model
t = Transaction("A2", "Example Corp", txn["Amount_Paid"], "US Dollar", is_laundering=1)
print("\n--- transaction ---")
print(t.summary())
print("is_large:", t.is_large())
print("is_reportable:", t.is_reportable())

# 4. Bitcoin transactions are always reportable, regardless of amount
btc = BitcoinTransaction("A9", "Wallet 9", 0.01, "Bitcoin", is_laundering=0)
print("\n--- bitcoin transaction ---")
print("is_reportable (always True for BTC):", btc.is_reportable())

# 5. Run the SQL-based fraud checks against the loaded table
print("\n--- velocity check (accounts with > 50 transactions) ---")
print(flag_velocity(con, max_count=50).head())

print("\n--- benford's law check ---")
print(benford_check(con))
