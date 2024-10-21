import sys
import csv
import heapq
import copy
import logging
from datetime import datetime, timedelta
from functools import cmp_to_key

from parse import parse_config, parse_transactions
from tax_methods import tax_methods
from accountant import Accountant

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def main(transactions_filepath, config_filepath):
    accountants = []
    for [tax_method_name, tax_method_comparartor] in tax_methods:
        accountants.append(Accountant(tax_method_name, tax_method_comparartor))
    global last_transaction_price
    last_transaction_price = None

    def on_new_transaction(transaction_type, transaction):
        for accountant in accountants:
            accountant.account_for_transaction(transaction_type, copy.copy(transaction))
            global last_transaction_price
            last_transaction_price = transaction.cost_basis

    parse_transactions(transactions_filepath, config_filepath, on_new_transaction)
    print_results(accountants, last_transaction_price)


def print_results(accountants, last_transaction_price):
    table_rows = []
    table_rows.append(["Method Name", "Current Profit", "Total Profit"])
    for accountant in accountants:
        tax_method_name = accountant.tax_method_name
        current_profit = accountant.get_profit()
        accountant.sell_all_transactions(last_transaction_price)
        total_unrealized_profits = accountant.get_profit()
        table_rows.append(
            [
                tax_method_name,
                "{:.2f}".format(current_profit),
                "{:.2f}".format(total_unrealized_profits),
            ]
        )
    print_table(table_rows, spacing=20)


def print_table(data, spacing=1):
    max_column_size = []
    for row_index in range(len(data)):
        for col_index in range(len(data[row_index])):
            data_length = len(data[row_index][col_index])
            if len(max_column_size) == col_index:
                max_column_size.append(data_length)
            else:
                max_column_size[col_index] = max(
                    data_length, max_column_size[col_index]
                )

    for row in data:
        row_string = ""
        for col_index, col in enumerate(row):
            row_string += str(col).rjust(max_column_size[col_index] + spacing)
        print(row_string)


if __name__ == "__main__":
    transaction_filepath = sys.argv[1]
    config_filepath = sys.argv[2]
    main(transaction_filepath, config_filepath)
