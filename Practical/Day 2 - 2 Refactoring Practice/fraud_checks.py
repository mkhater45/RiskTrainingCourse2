txn1 = {'Receiving_Currency':'US Dollar',
       'Amount_Received':9999}

txn2 = {'Receiving_Currency':'Rupee',
       'Amount_Received':10^6}
       

# #Check for US Dollar
# if txn1['Receiving_Currency'] == 'US Dollar':
#     print('US Dollar Check:')
#     if txn1['Amount_Received'] < 10000 and txn1['Amount_Received'] >= 9900:
#         print('Possible Fraud!')

# # Check for Yen
# if txn1['Receiving_Currency'] == 'Yen':
#     print('Yen Check:')
#     if txn1['Amount_Received'] < 1582140 and txn1['Amount_Received'] >= 1582140*.90:
#         print('Possible Fraud!')
        
# # Check for Rupee
# if txn1['Receiving_Currency'] == 'Rupee':
#     print('Rupee Check:')
#     if txn1['Amount_Received'] < 952058.50 and txn1['Amount_Received'] >= 952058.50*.90:
#         print('Possible Fraud!')

# Task: refactor the code above to make it more modular
# Create two files: 
# 1- main.py: defines txn1 and txn2 and makes any calls from the file fraud_checks.py
# 2- fraud_checks.py : the actual checks 



# Hint: You can use the following dictionary in fraud_checks.py to make currency conversion to USD easier:
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

# Example usage:
amount_in_euro = 100
amount_in_usd = amount_in_euro * to_usd_factors["Euro"]

def check_fruad(txn):
    usd_value = to_usd_factors[txn['Receiving_Currency']]*txn['Amount_Received']
    print(txn['Receiving_Currency'] + " Check:")
    if usd_value <10000 and usd_value > 9900:
        print('Possible Fraud!')
    else:
        print("not possible fraud")