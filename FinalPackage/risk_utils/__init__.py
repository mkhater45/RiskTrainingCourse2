#1. Documentation String
"""risk_utils: shared risk-analysis utilities for the training program.

The triple-quoted string at the very top is a standard docstring. 
It gives anyone looking at the package a quick history and summary of what it does—in this case, 
it is a collection of risk-analysis utilities built during a training program across "Day 2" and "Day 3".
"""

# 2. Relative Imports (The Bundling)
# The from .[module] import ... syntax uses relative imports (indicated by the leading dot .). 
# This means "look inside the current directory."It pulls specific tools from separate files and makes them available at the root level:
# Without this section: A user would have to type: from risk_utils.validation import validate_transaction
# With this section: a user can simply type: from risk_utils import validate_transaction, benford_check
    
from .models import Transaction, BitcoinTransaction
from .decorators import timer, log_call
from .validation import (
    check_positive_amount,
    check_required_fields,
    zscore_tag,
    validate_transaction,
)
from .fraud import flag_velocity, benford_check, BENFORD_EXPECTED_PCT
from .io import load_csv_folder, load_excel_folder, load_folder

# 3. Package Version
# This is a Python standard convention. It allows other programs or developers to 
# easily check what version of the package is currently installed by running 
# import risk_utils; 
# print(risk_utils.__version__)

__version__ = "0.1.0"

# 4. Public API Control (__all__)
# The __all__ list explicitly defines the whitelist for the package.
# It tells the developer exactly which objects are considered stable, public, and safe to use.
# If a user types from risk_utils import *, only the items listed inside this __all__ array will be imported into their script. 
# Anything left out of this list remains hidden from wildcard imports.

__all__ = [
    "Transaction",
    "BitcoinTransaction",
    "timer",
    "log_call",
    "check_positive_amount",
    "check_required_fields",
    "zscore_tag",
    "validate_transaction",
    "flag_velocity",
    "benford_check",
    "BENFORD_EXPECTED_PCT",
    "load_csv_folder",
    "load_excel_folder",
    "load_folder"
]
