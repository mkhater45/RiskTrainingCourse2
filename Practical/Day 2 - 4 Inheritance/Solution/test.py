from models import Transaction, BitcoinTransaction

firstTransaction = Transaction(account_number = "A1234", 
                               account_name = "Midwest Bank", 
                               amount = 9999, 
                               currency = "US Dollar", 
                               is_laundering=1)
print("firstTransaction.is_large(): " + str(firstTransaction.is_large()) )
print("firstTransaction.is_reportable() " + str(firstTransaction.is_reportable()) )


secondTransaction = Transaction(account_number = "A1234", 
                               account_name = "Midwest Bank", 
                               amount = 10**7, 
                               currency = "Yen", 
                               is_laundering=0)
print("secondTransaction.is_large(): " + str(secondTransaction.is_large()) )
                         
                         
thirdTransaction = BitcoinTransaction(account_number = "A1234", 
                               account_name = "Midwest Bank", 
                               amount = 1, 
                               currency = "Bitcoin", 
                               is_laundering=1)
print("thirdTransaction.is_large(): " + str(thirdTransaction.is_large()) )
print("thirdTransaction.is_reportable() " + str(thirdTransaction.is_reportable()) )