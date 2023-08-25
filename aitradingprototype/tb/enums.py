from enum import Enum


class TradingError(Enum):
    NOTIONAL_FILTER = "Filter failure: NOTIONAL, the minimum quantity should be {}."


class OrderAction(Enum):
    SKIP_ORDER = "Skip order, reason is '{}'."
    AVOID_ORDER = "Avoid placing unwanted order, reason is '{}'."
    POST_ORDER = "Post order."


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
