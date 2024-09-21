class Transaction:
    def __init__(self, transaction_size, cost_basis, datetime):
        self.transaction_size = transaction_size
        self.cost_basis = cost_basis
        self.datetime = datetime


    def __repr__(self):
        return f"{self.datetime} size: {self.transaction_size} cost: {self.cost_basis}"

    def __eq__(self, transaction2):
        return self.transaction_size == transaction2.transaction_size and \
               self.cost_basis == transaction2.cost_basis and \
               self.datetime == transaction2.datetime