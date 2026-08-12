from datetime import datetime

# Multipliers to convert 1 unit of foreign currency into USD (approximate rates)
to_usd_factors = {
    "US Dollar": 1.0,
    "Euro": 1.08,
    "Yuan": 0.14,
    "Yen": 0.0065,
    "Rupee": 0.012,
    "Ruble": 0.011,
    "UK Pound": 1.27,
    "Canadian Dollar": 0.74,
    "Mexican Peso": 0.058,
    "Australian Dollar": 0.65,
    "Brazil Real": 0.18,
    "Swiss Franc": 1.13,
    "Shekel": 0.27,
    "Saudi Riyal": 0.27
}

class Transaction:
    """A flagged transaction, with the context needed to act on it."""

    def __init__(self, account_number, account_name, amount, currency, is_laundering, timestamp=None):
        self.account_number = account_number
        self.account_name = account_name
        self.amount = amount
        self.currency = currency
        self.is_laundering = bool(is_laundering)
        self.timestamp = timestamp or datetime.now()

    def summary(self):
        flag = "LAUNDERING" if self.is_laundering else "Not Laundering"
        return f"[{flag}] account={self.account_number} amount={self.amount}"
        


#Task:
# Add a method, is_large(), that returns True if the amount is above USD 10,000 
# Add a method, is_reportable(), that returns True if the Transaction is both large and flagged as laundering



#Testing

# create a transaction class
myTransaction = Transaction(account_number = "515771",
                            account_name = "AB Corporation",
                            amount = 11000,
                            currency = "Euro",
                            is_laundering = True)

#print(myTransaction.is_large())
#print(myTransaction.is_reportable())
