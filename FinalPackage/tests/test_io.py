import pandas as pd

from risk_utils.io import load_csv_folder, load_excel_folder, load_folder


def test_load_csv_folder_loads_all_matching_files(tmp_path):
    pd.DataFrame({"account": ["A1"], "amount_paid": [100]}).to_csv(
        tmp_path / "a.csv", index=False
    )
    pd.DataFrame({"account": ["A2"], "amount_paid": [200]}).to_csv(
        tmp_path / "b.csv", index=False
    )

    con = load_csv_folder(str(tmp_path), db_path=":memory:")
    result = con.sql("SELECT * FROM transactions ORDER BY account").df()

    assert list(result["account"]) == ["A1", "A2"]
    assert list(result["amount_paid"]) == [100, 200]


def test_load_excel_folder_appends_to_existing_table(tmp_path):
    pd.DataFrame({"account": ["A1"], "amount_paid": [100]}).to_csv(
        tmp_path / "a.csv", index=False
    )
    pd.DataFrame({"account": ["A3"], "amount_paid": [300]}).to_excel(
        tmp_path / "c.xlsx", index=False
    )

    con = load_csv_folder(str(tmp_path), db_path=":memory:")
    load_excel_folder(str(tmp_path), con)
    result = con.sql("SELECT * FROM transactions ORDER BY account").df()

    assert list(result["account"]) == ["A1", "A3"]


def test_load_folder_combines_csv_and_excel_in_one_call(tmp_path):
    pd.DataFrame({"account": ["A1"], "amount_paid": [100]}).to_csv(
        tmp_path / "a.csv", index=False
    )
    pd.DataFrame({"account": ["A2"], "amount_paid": [200]}).to_excel(
        tmp_path / "b.xlsx", index=False
    )

    con = load_folder(str(tmp_path), db_path=":memory:")
    result = con.sql("SELECT * FROM transactions ORDER BY account").df()

    assert list(result["account"]) == ["A1", "A2"]
    assert list(result["amount_paid"]) == [100, 200]


def test_load_csv_folder_handles_spaces_in_folder_and_file_names(tmp_path):
    # the real course data ships as "TXNS 20220901 01.csv" - filenames and
    # folder paths with spaces must not break the glob-based SQL load
    spaced_dir = tmp_path / "bank data"
    spaced_dir.mkdir()
    pd.DataFrame({"account": ["A1"], "amount_paid": [100]}).to_csv(
        spaced_dir / "txns 01.csv", index=False
    )

    con = load_csv_folder(str(spaced_dir), db_path=":memory:")
    result = con.sql("SELECT * FROM transactions").df()

    assert list(result["account"]) == ["A1"]
