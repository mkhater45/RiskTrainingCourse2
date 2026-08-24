import fraud_checks
txn1 = {'Receiving_Currency':'US Dollar',
       'Amount_Received':9999}

txn2 = {'Receiving_Currency':'Rupee',
       'Amount_Received':10**6}

fraud_checks.check_fruad(txn1)
fraud_checks.check_fruad(txn2)