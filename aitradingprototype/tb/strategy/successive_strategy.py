import logging

from aitradingprototype.common.enums import Sentiment
from aitradingprototype.tb.enums import OrderAction, OrderSide, OrderType
from aitradingprototype.tb.strategy import Strategy

logger = logging.getLogger(__name__)


class SuccessiveStrategy(Strategy):
    """
    Successive Strategy
    -------------------
    Based on the received sentiment, the strategy will decide whether to place an order or not.
    The strategy logic is:
        - BUY order, when sentiment is `bullish` and `total_quantity_limit` won't be exceeded.
        - SELL order, when sentiment is `bearish` and we have `holding_quantity` to sell.
        - Skip order, when the above conditions are not met or when the sentiment is `unknown`/invalid.
    Note:
        - The strategy is designed to be used with a single trading pair.
        - `total_quantity_limit` - The upper limit on the total quantity of base asset that can be held via the accumulation of BUY orders at any given point.
        - `holding_quantity` - The total base asset quantity that is incremented or decremented by trades net quantity.
    """

    def __init__(self, trading_specs: dict):
        super().__init__(trading_specs)
        self.symbol = trading_specs["symbol"]
        self.order_qty = trading_specs["order_quantity"]
        self.total_qty_limit = trading_specs["total_quantity_limit"]

    def order_strategy(self, sentiment: str, holding_quantity: float) -> dict:
        """
        This method implements the strategy logic mentioned in the class docstring.
        If strategy is to place order, returns `OrderAction.POST_ORDER` with the order arguments.
        If strategy is to skip placing order, returns `OrderAction.SKIP_ORDER` with a reason.
        """

        if sentiment == Sentiment.BULLISH.value:
            if (holding_quantity + self.order_qty) <= self.total_qty_limit:
                return {
                    "action": OrderAction.POST_ORDER,
                    "order": {
                        "symbol": self.symbol,
                        "side": OrderSide.BUY.value,
                        "type": OrderType.MARKET.value,
                        "quantity": self.order_qty,
                    },
                }
            else:
                return {
                    "action": OrderAction.SKIP_ORDER,
                    "reason": OrderAction.SKIP_ORDER.value.format(
                        "the total quantity limit ({}) is, or would be, exceeded".format(
                            self.total_qty_limit
                        )
                    ),
                }

        elif sentiment == Sentiment.BEARISH.value:
            if holding_quantity - self.order_qty >= 0:
                return {
                    "action": OrderAction.POST_ORDER,
                    "order": {
                        "symbol": self.symbol,
                        "side": OrderSide.SELL.value,
                        "type": OrderType.MARKET.value,
                        "quantity": self.order_qty,
                    },
                }
            else:
                return {
                    "action": OrderAction.SKIP_ORDER,
                    "reason": OrderAction.SKIP_ORDER.value.format(
                        "holding quantity {} is not enough to sell".format(
                            holding_quantity
                        )
                    ),
                }
        else:
            return {
                "action": OrderAction.SKIP_ORDER,
                "reason": OrderAction.SKIP_ORDER.value.format(
                    "sentiment is {}".format(sentiment)
                ),
            }
