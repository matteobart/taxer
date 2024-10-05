import csv
import argparse
from datetime import datetime
from dataclasses import dataclass
import re
from pprint import pprint
import copy

REGEX_STRING_PATTERN = r"(\d{2}\/\d{2}\/\d{4})"
MONTH_YEAR_FORMAT = "%m/%Y"


@dataclass
class EquityData:
    date: datetime
    vesting_price: float
    number_of_shares_sold_for_taxes: str


@dataclass
class CSVData:
    fieldnames: list[str]
    data: list[any]


def remove_indexes_from_list(values, indexes_to_remove):
    indexes_to_remove.sort(reverse=True)
    for index_to_remove in indexes_to_remove:
        values.pop(index_to_remove)


def get_existing_transactions_file(transacations_path):
    with open(transacations_path, "r") as transactions_file:
        reader = csv.DictReader(transactions_file)
        fieldnames = reader.fieldnames
        data = []
        for row in reader:
            data.insert(0, row)
        return CSVData(fieldnames, data)


# cancel sell is an odd case... why is Schwab Canceling Sells that have already happened
# cancel sell needs to remove the previous sale item with corresponding values
def remove_cancelled_sells(transactions):
    indexes_to_remove = []
    for i, transaction in enumerate(transactions):
        if transaction.get("Action") == "Cancel Sell":
            index_to_remove = None
            for j in range(i - 1, -1, -1):
                if (
                    transactions[j]["Amount"] == transaction["Amount"][1:]
                    and transactions[j]["Quantity"] == transaction["Quantity"]
                ):
                    # can check the month/year here as well
                    index_to_remove = j
                    break
            if index_to_remove is None:
                print(f"Missing corresponding Sell for Cancel Sell {transaction}")
            else:
                # remove the sell that was cancelled
                indexes_to_remove.append(index_to_remove)
                # remove the cancel sell transaction
                indexes_to_remove.append(i)
    remove_indexes_from_list(transactions, indexes_to_remove)


def update_transaction_date(transaction):
    date_str_raw = transaction.get("Date")
    regex_search_result = re.findall(REGEX_STRING_PATTERN, date_str_raw)
    # todo: what values should we be using here
    # if len(regex_search_result) == 2:
    #     date_str = regex_search_result[1]
    # else:
    #     date_str = regex_search_result[0]
    date_str = regex_search_result[0]
    date = date_parse(date_str)
    transaction["Date"] = date_str


def update_transaction_price_for_vesting(
    transaction, tax_transactions_activity, fair_value_price_dict
):
    month_year_str = date_parse(transaction.get("Date")).strftime(MONTH_YEAR_FORMAT)
    number_of_shares_sold = transaction.get("Quantity")
    number_of_shares_sold_for_taxes_list = tax_transactions_activity.get(
        month_year_str, []
    )
    if number_of_shares_sold in number_of_shares_sold_for_taxes_list:
        number_of_shares_sold_for_taxes_list.remove(number_of_shares_sold)
        return True

    vesting_price = fair_value_price_dict.get(month_year_str)
    if vesting_price is None:
        print(f"Missing vesting price data for {month_year_str}")
    else:
        transaction["Price"] = f"${vesting_price}"
    return False


def remove_shares_sold_for_taxes(transaction, tax_transactions_sell):
    month_year_str = date_parse(transaction.get("Date")).strftime(MONTH_YEAR_FORMAT)
    number_of_shares_sold = transaction.get("Quantity")
    number_of_shares_sold_for_taxes_list = tax_transactions_sell.get(month_year_str, [])
    if number_of_shares_sold in number_of_shares_sold_for_taxes_list:
        number_of_shares_sold_for_taxes_list.remove(number_of_shares_sold)
        return True
    return False


def update_transactions(transactions, fair_value_price_dict, tax_transactions_dict):
    tax_transactions_sell = copy.deepcopy(tax_transactions_dict)
    tax_transactions_activity = copy.deepcopy(tax_transactions_dict)
    indexes_to_remove = []

    for i, transaction in enumerate(transactions):
        update_transaction_date(transaction)

        if transaction.get("Action") == "Stock Plan Activity":
            should_remove_transaction = update_transaction_price_for_vesting(
                transaction, tax_transactions_activity, fair_value_price_dict
            )
            if should_remove_transaction:
                indexes_to_remove.append(i)
        elif transaction.get("Action") == "Sell":
            should_remove_transaction = remove_shares_sold_for_taxes(
                transaction, tax_transactions_sell
            )
            if should_remove_transaction:
                indexes_to_remove.append(i)
    remove_indexes_from_list(transactions, indexes_to_remove)
    print(tax_transactions_sell)
    print(tax_transactions_activity)


def write_transaction_file(transactions, fieldnames, transactions_file_path):
    with open(transactions_file_path, "w") as transactions_file:
        writer = csv.DictWriter(transactions_file, fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)


def read_equity_transactions_file(equity_transactions_path):
    equity_data = []
    with open(equity_transactions_path, "r") as f:
        reader = csv.DictReader(f)
        try:
            while True:
                stock_information = next(reader)
                rsu_information = next(reader)
                date = date_parse(stock_information.get("Date"))
                fair_market_price = float(
                    rsu_information.get("FairMarketValuePrice").replace("$", "")
                )
                number_of_shares_sold_for_taxes = rsu_information.get(
                    "SharesSoldWithheldForTaxes"
                )
                data = EquityData(
                    date, fair_market_price, number_of_shares_sold_for_taxes
                )
                equity_data.append(data)
        except StopIteration:
            pass
    return equity_data


def get_vesting_price_dict(equity_data):
    fair_value_price_dict = {}
    for equity_item in equity_data:
        month_year_str = equity_item.date.strftime(MONTH_YEAR_FORMAT)
        if (
            fair_value_price_dict.get(month_year_str, equity_item.vesting_price)
            != equity_item.vesting_price
        ):
            print(
                f"Unexpected price mismatch for month: {month_year_str}. "
                "Vesting price across the month should match."
            )
        fair_value_price_dict[month_year_str] = equity_item.vesting_price
    return fair_value_price_dict


def get_tax_transactions_dict(equity_data):
    tax_transactions_dict = {}
    for equity_item in equity_data:
        month_year_str = equity_item.date.strftime(MONTH_YEAR_FORMAT)
        current_month_transactions = tax_transactions_dict.get(month_year_str, [])
        current_month_transactions.append(equity_item.number_of_shares_sold_for_taxes)
        tax_transactions_dict[month_year_str] = current_month_transactions
    return tax_transactions_dict


def main(transacations_path, equity_transactions_path, output_filepath):
    equity_transactions_data = read_equity_transactions_file(equity_transactions_path)
    vesting_price_dict = get_vesting_price_dict(equity_transactions_data)
    tax_transactions_dict = get_tax_transactions_dict(equity_transactions_data)
    print(tax_transactions_dict)
    csv_data = get_existing_transactions_file(transacations_path)
    transactions = csv_data.data
    fieldnames = csv_data.fieldnames
    remove_cancelled_sells(transactions)
    update_transactions(transactions, vesting_price_dict, tax_transactions_dict)
    write_transaction_file(transactions, fieldnames, output_filepath)


def date_parse(date_str):
    return datetime.strptime(date_str, "%m/%d/%Y")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transactions_path", required=True)
    parser.add_argument("-e", "--equity_transactions_path", required=True)
    parser.add_argument("-o", "--output", required=True)

    args = parser.parse_args()
    main(args.transactions_path, args.equity_transactions_path, args.output)
