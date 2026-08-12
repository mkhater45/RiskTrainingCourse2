"""Bulk-load a folder of CSV/Excel exports into a local DuckDB database.

Day 3: real risk data doesn't arrive as one clean file - it's a folder
of monthly CSV and Excel exports from different source systems. This
module automates the load with `glob` + DuckDB instead of doing it by
hand every month.
"""

import glob

import duckdb
import pandas as pd


def load_csv_folder(folder_path, db_path="risk.duckdb"):
    """Load every CSV in folder_path into a `transactions` table.

    Requires at least one matching CSV file. Connects to db_path on disk
    (not memory) so the data survives after the script ends.
    """
    con = duckdb.connect(db_path)
    con.sql(f"""
        CREATE OR REPLACE TABLE transactions AS
        SELECT * FROM read_csv_auto('{folder_path}/*.csv')
    """)
    return con


def load_excel_folder(folder_path, con):
    """Append every .xlsx in folder_path to the `transactions` table.

    DuckDB can't glob-read Excel directly, so this loops with pandas.
    """
    for path in glob.glob(f"{folder_path}/*.xlsx"):
        df = pd.read_excel(path)
        con.sql("INSERT INTO transactions SELECT * FROM df")
    return con


def load_folder(folder_path, db_path="risk.duckdb"):
    """Load both CSV and Excel files in folder_path into one table."""
    con = load_csv_folder(folder_path, db_path)
    load_excel_folder(folder_path, con)
    return con
