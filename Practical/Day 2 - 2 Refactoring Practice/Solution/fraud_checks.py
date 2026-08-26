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

def check_amount(amount, currency):
       
    amount_in_usd = amount * to_usd_factors[currency]
    print(f"{amount_in_usd} USD: ",end="")
    if amount_in_usd < 10000 and amount_in_usd >= 9900:
        print('Possible Fraud!')
    else:
        print("No fraud suspected")

    return True

# Adding more currency checks is merely adding one line to the factors dictionary