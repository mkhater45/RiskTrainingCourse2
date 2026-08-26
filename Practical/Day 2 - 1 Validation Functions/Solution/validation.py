def check_positive_amount(amount):
    """Raise if amount is not a positive number."""
    if amount <= 0:
        raise ValueError(f"amount_paid must be positive, got {amount}")
    return True


def check_required_fields(txn, required=("Account", "Amount_Paid", "Timestamp")):
    """Raise if txn is missing any required field."""
    
    for field in required:
        if field not in txn.keys():
            raise ValueError(f"required field {field} missing")
        
    return True
    
# validate a transaction
# A transaction is represented as a Python dictionary
def validate_transaction(txn):
    """Run every check on a single transaction. Raises on first failure."""
    check_positive_amount(txn["Amount_Paid"])
    check_required_fields(txn)
    return True
    
 
# Define a transaction and validate it 
myTransaction = {"Amount_Paid":5,
                "Account":"Acc1234",
                "Timestamp":"2025-05-017 12:14:56"
                }

validate_transaction(myTransaction)