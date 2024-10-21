import csv
import json
import logging
from datetime import datetime

from transaction import Transaction
from constants import *


logger = logging.getLogger()


def parse_config(filepath):
    with open(filepath) as f:
        config = json.load(f)
        # todo: add a bunch of error checking here for the various required files
        return config


def parse_transactions(transactions_filepath, config_filepath):
    config = parse_config(config_filepath)
    if not config:
        raise Exception("Bad configuration input")

    with open(transactions_filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            transaction = parse_transaction(row, config, i + 2)
            if not transaction:
                continue
            yield transaction


def parse_transaction(transaction_row, config, line_number):
    if transaction_row.get(config[TICKER_COLUMN_KEY]) != config[TICKER_TO_TRACK_KEY]:
        logger.info(
            f"Skipping line number {line_number} - unrelated transaction to ticker"
        )
        return
    transaction_type = transaction_row.get(config[TRANSACTION_TYPE_KEY])
    if transaction_type not in config.get(
        TRANSACTION_BUY_VALUE, []
    ) and transaction_type not in config.get(TRANSACTION_SELL_VALUE, []):
        logger.info(f"Skipping line number {line_number} - unrelated transaction type")
        return
    # transaction datetime
    datetime_raw = transaction_row.get(config[DATE_COLUMN_KEY])
    datetime_format = config[DATE_FORMAT_KEY]
    if not datetime_raw:
        logger.error(f"Datetime not found on line {line_number}")
        return None

    datetime_value = datetime.strptime(datetime_raw, datetime_format)
    if not datetime_value:
        logger.error(
            f"Datetime ({datetime_raw}) unable to be parsed by {datetime_format} on line {line_number}"
        )
        return None

    # transaction size
    transaction_size_raw = transaction_row.get(config[QUANTITY_COLUMN_KEY])
    if not transaction_size_raw:
        logger.error(f"Quantity not found on line {line_number}")
        return None
    try:
        transaction_size_value = int(transaction_size_raw)
    except ValueError:
        logger.error(
            f"Quantity ({transaction_size_raw}) is not an integer value on line {line_number}"
        )
        return None

    # transaction cost
    cost_basis_raw = transaction_row.get(config[SECURITY_PRICE_COLUMN_KEY])
    if not cost_basis_raw:
        logger.error(f"Transaction cost not found on line {line_number}")
        return None
    cost_basis_raw_number = cost_basis_raw.replace("$", "")
    try:
        cost_basis_value = float(cost_basis_raw_number)
    except ValueError:
        logger.error(
            f"Security price ({cost_basis_raw_number}) is not a number on line {line_number}"
        )
        return None

    # transaction type
    transaction_type_raw = transaction_row.get(config[TRANSACTION_TYPE_KEY])
    if transaction_type_raw in config[TRANSACTION_BUY_VALUE]:
        transaction_type_value = TRANSACTION_BUY
    elif transaction_type_raw in config[TRANSACTION_SELL_VALUE]:
        transaction_type_value = TRANSACTION_SELL
    else:
        logger.error(
            f"Transaction type ({transaction_type_raw}) is not defined in the config on line {line_number}"
        )
        return None

    transaction = Transaction(
        transaction_size_value, cost_basis_value, datetime_value, transaction_type_value
    )
    logger.debug(f"{transaction_type_value} {transaction} on line {line_number}")
    return transaction
