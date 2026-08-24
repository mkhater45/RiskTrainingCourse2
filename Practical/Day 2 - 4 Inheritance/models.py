from datetime import datetime

class CurrencyConverter:
    def __init__(self):
        self.__to_usd_factors__ = {
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
        "Saudi Riyal": 0.27,
        "Bitcoin":70000}
        
    def toUSD(self,amount,base_currency):
        if base_currency in self.__to_usd_factors__.keys():
            return self.__to_usd_factors__[base_currency]*amount
        else:
            raise ValueError("Unknown Currency "+base_currency)

class Transaction:
    """A flagged transaction, with the context needed to act on it."""

    def __init__(self, account_number, account_name, amount, currency, is_laundering, timestamp=None):
        self.account_number = account_number
        self.account_name = account_name
        self.amount = amount
        self.currency = currency
        self.is_laundering = bool(is_laundering)
        self.timestamp = timestamp or datetime.now()
        self.__converter__ = CurrencyConverter()

    def summary(self):
        flag = "LAUNDERING" if self.is_laundering else "Not Laundering"
        return f"[{flag}] account_number={self.account_number} amount={self.amount}"
        
    def is_large(self):
        return self.__converter__.toUSD(self.amount,self.currency) > 10000
        
    def is_reportable(self):
        return (self.is_large() and self.is_laundering)
        
class BitcoinTransaction(Transaction):
    """A flagged transaction, with the context needed to act on it."""

    def __init__(self, account_number, account_name, amount, currency, is_laundering, timestamp=None):
        super().__init__(account_number, account_name, amount, currency, is_laundering, timestamp=None)
        
        if self.currency.lower() != "bitcoin":
            raise ValueError("Cannot create a Bitcoin transaction from a non-bitcoin currency!")
          
    def summary(self):
        flag = "LAUNDERING" if self.is_laundering else "Not Laundering"
        return f"[{flag}] account_number={self.account_number} amount={self.amount}"
    
    def is_large(self):
        return self.__converter__.toUSD(self.amount,self.currency) > 10000
        
    def is_reportable(self):
        return True

#Task:
# use inheritance to simplify the code of BitcoinTransaction and improve modularity
# Note that is_reportable() for Bitcoin transactions is always True
