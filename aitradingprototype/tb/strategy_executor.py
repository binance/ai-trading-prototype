import logging

from aitradingprototype.common import RedisClient
from aitradingprototype.tb import BinanceClient
from aitradingprototype.tb.enums import OrderAction, OrderSide

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """
    Strategy Executor
    -----------------
    This class is responsible for executing the strategy, which can be either to place an order or skip it.
    If the strategy is to place an order, it will place a market order to Binance Spot Market and update the base asset holding quantity in Redis.

    Note:
        "holding quantity" - The total base asset quantity that is incremented or decremented by trades net quantity.
    """

    def __init__(
        self, binance: BinanceClient, redis: RedisClient, holding_qty_key: str
    ):
        self.binance = binance
        self.redis = redis
        # total base asset quantity the account is currently holding for this bot's strategy
        self.holding_qty_key = holding_qty_key

    def _calc_net_quantity(self, order_response) -> float:
        """
        Calculate net quantity from a sucessful market order response
        """
        executed_qty = float(order_response["executedQty"])
        commission = sum(float(fill["commission"]) for fill in order_response["fills"])
        return executed_qty - commission

    def _response_handler(self, order_response) -> None:
        """
        Update the base asset holding quantity in Redis based on the order response from Binance API.
        """
        net_qty = self._calc_net_quantity(order_response)
        if order_response["side"] == OrderSide.BUY.value:
            logger.debug(f"Increment Redis {self.holding_qty_key}: {net_qty}")
            self.redis.increment_key(self.holding_qty_key, net_qty)
        else:
            logger.debug(f"Decrement Redis {self.holding_qty_key}: {net_qty}")
            self.redis.decrement_key(self.holding_qty_key, net_qty)

    def holding_qty(self) -> float:
        """
        Return the current base asset holding quantity from Redis.
        """
        return float(self.redis.get_float_key(self.holding_qty_key))

    def execute_order(self, strategy_order: dict) -> None:
        """
        Execute order strategy.
        """
        if strategy_order["action"] == OrderAction.SKIP_ORDER:
            logger.info(strategy_order["reason"])
        elif strategy_order["action"] == OrderAction.POST_ORDER:
            response = self.binance.post_order(args=strategy_order["order"])
            self._response_handler(response)
