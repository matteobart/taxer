import sys
import csv
import heapq
import copy
import logging
import argparse
from datetime import datetime, timedelta
from functools import cmp_to_key

from parse import parse_config, parse_transactions
from tax_methods import tax_methods
from accountant import Accountant
from constants import LAST_DATE_KEY, LAST_PRICE_KEY, CAPTIAL_GAINS_TAX_RATE_KEY, INCOME_TAX_RATE_KEY

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
    config = parse_config(config_filepath)
    # todo: check the config for None

    last_transaction_price = None
    last_transaction_datetime = None
    for transaction in parse_transactions(transactions_filepath, config):
        for accountant in accountants:
            accountant.account_for_transaction(copy.copy(transaction))
            last_transaction_price = transaction.cost_basis
            last_transaction_datetime = transaction.datetime
    if config.get(LAST_DATE_KEY) and config.get(LAST_PRICE_KEY):
        last_transaction_price = config.get(LAST_PRICE_KEY)
        last_transaction_datetime = config.get(LAST_DATE_KEY)

    print_results(accountants, last_transaction_price, last_transaction_datetime, config[CAPTIAL_GAINS_TAX_RATE_KEY], config[INCOME_TAX_RATE_KEY])


def print_results(accountants, last_transaction_price, last_transaction_datetime, capital_gains_tax_rate, income_tax_rate):
    table_rows = []
    table_rows.append(["Method Name", "Current Profit", "Total Short Term Profit", "Total Long Term Profit", "Total Tax Burden"])
    for accountant in accountants:
        tax_method_name = accountant.tax_method_name
        current_profit = accountant.get_profit()
        accountant.sell_all_transactions(last_transaction_price, last_transaction_datetime)
        total_unrealized_short_term_profits = accountant.get_short_term_profit()
        total_unrealized_long_term_profits = accountant.get_long_term_profit()
        total_tax_burden = "N/A"
        if capital_gains_tax_rate is not None and income_tax_rate is not None:
            if (total_unrealized_long_term_profits + total_unrealized_short_term_profits) <= 0:
                tax_burden_number = 0
            elif total_unrealized_long_term_profits > 0 and total_unrealized_short_term_profits > 0:
                tax_burden_number = total_unrealized_long_term_profits * capital_gains_tax_rate + total_unrealized_short_term_profits * income_tax_rate
            elif total_unrealized_long_term_profits > 0:
                tax_burden_number = (total_unrealized_long_term_profits - total_unrealized_short_term_profits) * capital_gains_tax_rate
            elif total_unrealized_short_term_profits > 0:
                tax_burden_number = (total_unrealized_short_term_profits - total_unrealized_long_term_profits) * income_tax_rate
            total_tax_burden = "{:.2f}".format(tax_burden_number)

        table_rows.append(
            [
                tax_method_name,
                "{:.2f}".format(current_profit),
                "{:.2f}".format(total_unrealized_short_term_profits),
                "{:.2f}".format(total_unrealized_long_term_profits),
                total_tax_burden
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
