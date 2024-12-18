import logging
from functools import cmp_to_key

from constants import TRANSACTION_BUY, TRANSACTION_SELL

logger = logging.getLogger()


class Accountant:
    def __init__(self, tax_method_name, tax_method_comparator):
        self.tax_method_name = tax_method_name
        self.tax_method_comparator = tax_method_comparator
        self.unsold_transactions = []
        self.short_term_profit_accumulator = 0
        self.long_term_profit_accumulator = 0

    def account_for_transaction(self, transaction):
        if transaction.transaction_type == TRANSACTION_BUY:
            self.unsold_transactions.append(transaction)
        elif transaction.transaction_type == TRANSACTION_SELL:
            tax_method_cmp = lambda x, y: self.tax_method_comparator(
                x, y, transaction.cost_basis, transaction.datetime
            )
            self.unsold_transactions = sorted(
                self.unsold_transactions, key=cmp_to_key(tax_method_cmp)
            )
            volume_left = transaction.transaction_size
            while volume_left > 0:
                transaction_to_sell = self.unsold_transactions.pop(0)
                volume = min(transaction_to_sell.transaction_size, volume_left)
                profit_accumulator = (
                    transaction.cost_basis - transaction_to_sell.cost_basis
                ) * volume
                if self.is_long_term(transaction_to_sell.datetime, transaction.datetime):
                    self.long_term_profit_accumulator += profit_accumulator
                else:
                    self.short_term_profit_accumulator += profit_accumulator
                if volume < transaction_to_sell.transaction_size:
                    transaction_to_sell.transaction_size -= volume
                    self.unsold_transactions.append(transaction_to_sell)
                volume_left -= volume
        else:
            logger.warning(
                f"Unknown transaction type passed: {transaction.transaction_type}"
            )

    def sell_all_transactions(self, current_price, current_datetime):
        for transaction in self.unsold_transactions:
            profit_accumulator = (
                current_price - transaction.cost_basis
            ) * transaction.transaction_size
            if self.is_long_term(transaction.datetime, current_datetime):
                self.long_term_profit_accumulator += profit_accumulator
            else:
                self.short_term_profit_accumulator += profit_accumulator
        self.unsold_transactions = []

    def get_profit(self):
        return self.short_term_profit_accumulator + self.long_term_profit_accumulator

    def get_short_term_profit(self):
        return self.short_term_profit_accumulator

    def get_long_term_profit(self):
        return self.long_term_profit_accumulator

    def get_tax_method_name(self):
        return self.tax_method_name

    def is_long_term(self, buy_transaction_datetime, sell_transaction_datetime):
        return (sell_transaction_datetime - buy_transaction_datetime).days > 365
