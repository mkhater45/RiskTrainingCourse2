# risk_utils

Shared risk-analysis utilities for the training program. Built across Day 2
(Python fundamentals, classes, decorators, design patterns) and Day 3
(validation, fraud checks, packaging, and publishing) of the course.

## Install

```bash
pip install -e .
```

For the test suite too:

```bash
pip install -e ".[dev]"
```

## What's inside

| Module | Contents |
|---|---|
| `models` | `Transaction`, `BitcoinTransaction` |
| `decorators` | `@timer`, `@log_call` |
| `validation` | `check_positive_amount`, `check_required_fields`, `zscore_tag`, `validate_transaction` |
| `fraud` | `flag_velocity`, `benford_check` — run as SQL against a DuckDB table |
| `io` | `load_csv_folder`, `load_excel_folder`, `load_folder` — glob + DuckDB bulk loading |

## Quickstart

```python
from risk_utils import flag_velocity, Transaction, load_folder

con = load_folder("data")                   # loads every CSV/XLSX in data/
con.sql("SELECT * FROM transactions").df()

flag_velocity(con)                       # DataFrame of accounts over the count threshold

```

See `examples/quickstart.py` for a full walkthrough that ties every module
together against the sample data in `data/`.

## Tests

```bash
pytest
```

## Versioning

`risk_utils` follows semantic versioning (MAJOR.MINOR.PATCH). Bump PATCH for
bug fixes, MINOR for backwards-compatible additions, MAJOR for breaking
changes — other courses install this package, so a careless bump breaks
someone else's class.
