import csv
import json
from transaction import Transaction
from datetime import datetime
import logging

DATE_COLUMN_KEY = "date_column"
DATE_FORMAT_KEY = "date_format"
TICKER_COLUMN_KEY = "ticker_column"
TICKER_TO_TRACK_KEY = "ticker_to_track"
QUANTITY_COLUMN_KEY = "quanitity_column"
SECURITY_PRICE_COLUMN_KEY = "security_price_column"
TRANSACTION_TYPE_KEY = "transaction_type_column"
TRANSACTION_BUY_VALUE = "transaction_buy_values"
TRANSACTION_SELL_VALUE = "transaction_sell_values"

logger = logging.getLogger('taxer')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

def parse_config(filepath):
    with open(filepath) as f:
        config = json.load(f)
    # todo: add a bunch of error checking here for the various required files
        return config


def parse_transactions(transactions_filepath, config_filepath, on_new_transaction):
    config = parse_config(config_filepath)
    if not config:
        return None

    with open(transactions_filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            transaction_tuple = parse_transaction(row, config, i+2)
            if not transaction_tuple:
                continue
            transaction_type, transaction = transaction_tuple
            on_new_transaction(transaction_type, transaction)


def parse_transaction(transaction_row, config, line_number):
    if transaction_row.get(config[TICKER_COLUMN_KEY]) != config[TICKER_TO_TRACK_KEY]:
        logger.debug(f"Skipping line number {line_number} - unrelated transaction to ticker")
        return
    transaction_type = transaction_row.get(config[TRANSACTION_TYPE_KEY]) 
    if (transaction_type not in config.get(TRANSACTION_BUY_VALUE, [])
        and transaction_type not in config.get(TRANSACTION_SELL_VALUE, [])):
        logger.debug(f"Skipping line number {line_number} - unrelated transaction type")
        return
    # transaction datetime
    datetime_raw = transaction_row.get(config[DATE_COLUMN_KEY])
    datetime_format = config[DATE_FORMAT_KEY]
    if not datetime_raw:
        print(f"Datetime not found on line {line_number}")
        return None

    datetime_value = datetime.strptime(datetime_raw, datetime_format)
    if not datetime_value:
        print(f"Datetime ({datetime_raw}) unable to be parsed by {datetime_format} on line {line_number}")
        return None
    
    # transaction size
    transaction_size_raw = transaction_row.get(config[QUANTITY_COLUMN_KEY])
    if not transaction_size_raw:
        print(f"Quantity not found on line {line_number}")
        return None
    try:
        transaction_size_value = int(transaction_size_raw)
    except ValueError:
        print(f"Quantity ({transaction_size_raw}) is not an integer value on line {line_number}")
        return None

    # transaction cost
    cost_basis_raw = transaction_row.get(config[SECURITY_PRICE_COLUMN_KEY])
    if not cost_basis_raw:
        print(f"Transaction cost not found on line {line_number}")
        return None
    cost_basis_raw_number = cost_basis_raw.replace("$", "")
    try:
        cost_basis_value = float(cost_basis_raw_number)
    except ValueError:
        print(f"Security price ({cost_basis_raw_number}) is not a number on line {line_number}")
        return None

    # transaction type
    transaction_type_raw = transaction_row.get(config[TRANSACTION_TYPE_KEY])
    if transaction_type_raw in config[TRANSACTION_BUY_VALUE]:
        transaction_type_value = "BUY"
    elif transaction_type_raw in config[TRANSACTION_SELL_VALUE]:
        transaction_type_value = "SELL"
    else:
        print(f"Transaction type ({transaction_type_raw}) is not defined in the config on line {line_number}")
        return None

    return transaction_type_value, Transaction(transaction_size_value, cost_basis_value, datetime_value)