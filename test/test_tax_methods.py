import unittest
from datetime import datetime
from tax_methods import (
    fifo_comparator,
    lifo_comparator,
    high_cost_comparator,
    low_cost_comparator,
    tax_optimizer_comparator,
)
from transaction import Transaction
from functools import cmp_to_key

transactions1 = [
    Transaction(10, 5, datetime(2024, 1, 1)),
    Transaction(20, 2, datetime(2024, 3, 1)),
    Transaction(30, 10, datetime(2024, 4, 1)),
]

transactions2 = [
    Transaction(30, 20, datetime(2020, 4, 1)),  # long term loss / larger
    Transaction(30, 15, datetime(2020, 4, 1)),  # long term loss / smaller
    Transaction(30, 8, datetime(2020, 4, 1)),  # long term gain / smaller
    Transaction(30, 1, datetime(2020, 4, 1)),  # long term gain / larger
    Transaction(10, 10, datetime(2020, 12, 30)),  # long term - break even
    Transaction(10, 11, datetime(2024, 1, 1)),  # short term loss / smaller
    Transaction(10, 7, datetime(2024, 1, 1)),  # short term gain / smaller
    Transaction(20, 3, datetime(2024, 3, 1)),  # short term gain / larger
    Transaction(20, 20, datetime(2024, 3, 1)),  # short term loss / larger
    Transaction(10, 10, datetime(2024, 12, 30)),  # short term - break even
]


class TestFIFO(unittest.TestCase):
    def test_fifo1_1(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: fifo_comparator(x, y, sell_price, sell_datetime)
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(30, 10, datetime(2024, 4, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_fifo1_2(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: fifo_comparator(x, y, sell_price, sell_datetime)
        transactions = transactions1.copy()
        transactions.reverse()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(30, 10, datetime(2024, 4, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)


class TestLIFO(unittest.TestCase):

    def test_lifo1_1(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: lifo_comparator(x, y, sell_price, sell_datetime)
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_lifo1_2(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: lifo_comparator(x, y, sell_price, sell_datetime)
        transactions = transactions1.copy()
        transactions.reverse()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)


class TestHighCost(unittest.TestCase):

    def test_highcost1_1(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: high_cost_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_highcost1_2(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: high_cost_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        transactions.reverse()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)


class TestLowCost(unittest.TestCase):

    def test_lowcost1_1(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: low_cost_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(30, 10, datetime(2024, 4, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_highcost1_2(self):
        sell_price = None
        sell_datetime = None
        tax_method_cmp = lambda x, y: low_cost_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        transactions.reverse()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(20, 2, datetime(2024, 3, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(30, 10, datetime(2024, 4, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)


class TestTaxOptimizer(unittest.TestCase):

    def test_taxoptimizer_singles_1(self):
        tenPrice = Transaction(1, 10, datetime(2024, 4, 1))
        fivePrice = Transaction(1, 5, datetime(2024, 4, 1))
        comparison_result = tax_optimizer_comparator(
            tenPrice, fivePrice, 5, datetime(2024, 4, 2)
        )
        self.assertEqual(comparison_result, -1)

        comparison_result_flipped = tax_optimizer_comparator(
            fivePrice, tenPrice, 5, datetime(2024, 4, 2)
        )
        self.assertEqual(comparison_result_flipped, 1)

    def test_taxoptimizer1_1(self):
        sell_price = 5
        sell_datetime = datetime(2025, 3, 10)
        tax_method_cmp = lambda x, y: tax_optimizer_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_taxoptimizer1_1(self):
        sell_price = 5
        sell_datetime = datetime(2025, 3, 10)
        tax_method_cmp = lambda x, y: tax_optimizer_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_taxoptimizer1_2(self):
        sell_price = 5
        sell_datetime = datetime(2025, 3, 10)
        tax_method_cmp = lambda x, y: tax_optimizer_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions1.copy()
        transactions.reverse()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(30, 10, datetime(2024, 4, 1)),
            Transaction(10, 5, datetime(2024, 1, 1)),
            Transaction(20, 2, datetime(2024, 3, 1)),
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

    def test_taxoptimizer2_1(self):
        sell_price = 10
        sell_datetime = datetime(2024, 12, 31)
        tax_method_cmp = lambda x, y: tax_optimizer_comparator(
            x, y, sell_price, sell_datetime
        )
        transactions = transactions2.copy()
        sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
        expected_transactions = [
            Transaction(20, 20, datetime(2024, 3, 1)),  # short term loss / larger
            Transaction(10, 11, datetime(2024, 1, 1)),  # short term loss / smaller
            Transaction(30, 20, datetime(2020, 4, 1)),  # long term loss / larger
            Transaction(30, 15, datetime(2020, 4, 1)),  # long term loss / smaller
            Transaction(10, 10, datetime(2024, 12, 30)),  # short term - break even
            Transaction(10, 10, datetime(2020, 12, 30)),  # long term - break even
            Transaction(30, 8, datetime(2020, 4, 1)),  # long term gain / smaller
            Transaction(30, 1, datetime(2020, 4, 1)),  # long term gain / larger
            Transaction(10, 7, datetime(2024, 1, 1)),  # short term gain / smaller
            Transaction(20, 3, datetime(2024, 3, 1)),  # short term gain / larger
        ]
        self.assertEqual(sorted_transactions, expected_transactions)

        def test_taxoptimizer2_2(self):
            sell_price = 10
            sell_datetime = datetime(2024, 12, 31)
            tax_method_cmp = lambda x, y: tax_optimizer_comparator(
                x, y, sell_price, sell_datetime
            )
            transactions = transactions2.copy()
            transactions = transactions.reverse()
            sorted_transactions = sorted(transactions, key=cmp_to_key(tax_method_cmp))
            expected_transactions = [
                Transaction(20, 20, datetime(2024, 3, 1)),  # short term loss / larger
                Transaction(10, 11, datetime(2024, 1, 1)),  # short term loss / smaller
                Transaction(30, 20, datetime(2020, 4, 1)),  # long term loss / larger
                Transaction(30, 15, datetime(2020, 4, 1)),  # long term loss / smaller
                Transaction(10, 10, datetime(2024, 12, 30)),  # short term - break even
                Transaction(10, 10, datetime(2020, 12, 30)),  # long term - break even
                Transaction(30, 8, datetime(2020, 4, 1)),  # long term gain / smaller
                Transaction(30, 1, datetime(2020, 4, 1)),  # long term gain / larger
                Transaction(10, 7, datetime(2024, 1, 1)),  # short term gain / smaller
                Transaction(20, 3, datetime(2024, 3, 1)),  # short term gain / larger
            ]
            self.assertEqual(sorted_transactions, expected_transactions)


if __name__ == "__main__":
    unittest.main()
