import sys
import csv
from datetime import datetime, timedelta
import heapq
from functools import cmp_to_key
from parse import parse_config, parse_transactions
from tax_methods import tax_methods
from accountant import Accountant
import copy

def main(transactions_filepath, config_filepath):
    accountants = []
    for [tax_method_name, tax_method_comparartor] in tax_methods:
        accountants.append(Accountant(tax_method_name, tax_method_comparartor))

    def on_new_transaction(transaction_type, transaction):
        for accountant in accountants:
            accountant.account_for_transaction(transaction_type, copy.copy(transaction))
    
    parse_transactions(transactions_filepath, config_filepath, on_new_transaction)
    for accountant in accountants:
        print(f"{accountant.tax_method_name}")
        print(f"{accountant.get_profit()}")

if __name__=="__main__":
    transaction_filepath = sys.argv[1] 
    config_filepath = sys.argv[2]
    main(transaction_filepath, config_filepath)
