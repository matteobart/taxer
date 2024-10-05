from datetime import timedelta

X_IS_GREATER = 1
Y_IS_GREATER = -1
X_AND_Y_EQUAL = 0


# Short-term losses => Lots reflecting short-term losses, from greatest short-term loss to least short-term loss
# Long-term losses => Lots reflecting long-term losses, from greatest long-term loss to least long-term loss
# Short-term, no gains nor losses => Short-term lots reflecting no gain nor loss
# Long-term, no gains nor losses => Long-term lots reflecting no gain nor loss
# Long-term gains => Lots reflecting long-term gains, from least long-term gain to greatest long-term gain
# Short-term gains => Lots reflecting short-terms gains, from least short-term gain to greatest short-term gain
def tax_optimizer_comparator(x, y, current_price, current_datetime):
    x_short_term = (current_datetime - x.datetime) <= timedelta(days=365)
    y_short_term = (current_datetime - y.datetime) <= timedelta(days=365)
    x_gain = current_price - x.cost_basis
    y_gain = current_price - y.cost_basis

    # losses before gain
    if x_gain < 0 and y_gain >= 0:
        return Y_IS_GREATER
    elif x_gain >= 0 and y_gain < 0:
        return X_IS_GREATER

    # no gain / nor loss
    if x_gain == 0 and y_gain != 0:
        return Y_IS_GREATER
    elif x_gain != 0 and y_gain == 0:
        return X_IS_GREATER

    # both is either loss or both is gain
    if x_gain > 0:  # both are gains
        if x_short_term and not y_short_term:
            return X_IS_GREATER
        elif not x_short_term and y_short_term:
            return Y_IS_GREATER
    elif x_gain <= 0:  # both are losses OR neither gain nor loss
        if x_short_term and not y_short_term:
            return Y_IS_GREATER
        elif not x_short_term and y_short_term:
            return X_IS_GREATER

    # both are also short term / long term
    if x_gain < y_gain:
        return Y_IS_GREATER
    elif x_gain > y_gain:
        return X_IS_GREATER

    return X_AND_Y_EQUAL


def fifo_comparator(x, y, current_price, current_datetime):
    return (x.datetime - y.datetime).total_seconds()


def lifo_comparator(x, y, current_price, current_datetime):
    return (y.datetime - x.datetime).total_seconds()


def high_cost_comparator(x, y, current_price, current_datetime):
    return y.cost_basis - x.cost_basis


def low_cost_comparator(x, y, current_price, current_datetime):
    return x.cost_basis - y.cost_basis


tax_methods = [
    ("fifo", fifo_comparator),
    ("lifo", lifo_comparator),
    ("tax-optimizer", tax_optimizer_comparator),
    ("high-cost", high_cost_comparator),
    ("low-cost", low_cost_comparator),
]
