from fraud_checks import check_amount

txn1 = {'Receiving_Currency':'US Dollar',
       'Amount_Received':9999}

txn2 = {'Receiving_Currency':'Rupee',
       'Amount_Received':10**5}
       

print("First Transaction:")
check_amount(txn1["Amount_Received"],txn1["Receiving_Currency"])

print("Second Transaction:")
check_amount(txn2["Amount_Received"],txn2["Receiving_Currency"])
