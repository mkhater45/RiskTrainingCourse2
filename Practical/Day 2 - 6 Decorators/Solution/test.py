from models import Transaction


#Task 1: Use the log_call decorator to log each call to Transaction.is_large()
#Task 2: Finish implementing the decorator "timer" in decorators.py and use it to time the call to is_reportable()

myTransaction = Transaction(account_number = "A1234", 
                               account_name = "Midwest Bank", 
                               amount = 9999, 
                               currency = "US Dollar", 
                               is_laundering=1)

myTransaction.is_large()
myTransaction.is_reportable()
