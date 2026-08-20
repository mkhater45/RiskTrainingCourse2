"""Project Task 1: test that the implementation actually works
"""

import sys
from pathlib import Path

# Make FinalPackage/ (the parent of this risk_utils/ folder) importable,
# so `risk_utils.io` resolves without needing `pip install -e .` first.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from risk_utils.io import load_folder

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

connection = load_folder(str(DATA_DIR))

result = connection.sql("select count(*) from transactions")

print(result)
