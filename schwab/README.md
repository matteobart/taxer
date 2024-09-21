# Schwab
If using Schwab for RSUs, the required data is spread out across multiple files. This code takes multiple data inputs and transforms it into a single output that can be fed into the main taxer logic. 

## Inputs
There are two files required:  
1. Equity Transactions
* this gives information about the cost basis of your stock & reveals how much stock was sold for taxes
* this information can be found by:
* logging on to Schwab -> Going to Accounts -> History -> Ensure you are on the Equity Award Center -> Update Date Range to get all data -> Click Search -> Click Export -> Choose CSV option

2. Transactions
* this gives the information on all your selling history, including sell dates, and prices
* this information can be found by:
* logging on to Schwab -> Going to Accounts -> History -> Ensure you are on the account where the RSUs go to -> Update Date Range to get all data -> Click Search -> Click Export -> Choose CSV option

## Run Example
```
python3 merge_schwab.py --equity_transactions_path /path/to/EquityAwardsCenter_Transactions_##############.csv -t /path/to/tick_XXXXXX_Transactions_########-######.csv -o /path/to/data.csv
```

## Logic
This code will do a few things to generate an output file including:
* Reverse transactions, such that oldest transactions are first
* Add Cost Basis information to the 'Stock Plan Activity' transactions
* Remove the shares that are immeditely sold for taxes (as they would mess with tax calculations as you have no control over them)
* Account for Cancel Sell transactions
