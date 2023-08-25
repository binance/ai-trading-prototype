from decimal import Decimal

from aitradingprototype.common.utils import round_up


class FilterManager:
    """
    Filter Manager
    --------------
    Class to manage the symbol's trading rules (Filters) according to Binance's /exchangeInfo endpoint.
    """

    def __init__(self, symbol, exchange_info):
        self.symbol = symbol
        self.exchange_info = exchange_info

    def _clamp_quantity(self, n, min_n, max_n):
        """
        Clamp n to max and min bounds
        """
        return min(max_n, max(min_n, n))

    def get_lot_size_filter(self):
        """
        Get LOT_SIZE filter from exchange info:
        {
            "filterType": "LOT_SIZE",
            "minQty": "0.00100000",
            "maxQty": "100000.00000000",
            "stepSize": "0.00100000" // intervals that a quantity/icebergQty can be increased/decreased by
        }
        """
        lot_size_filter = None
        for s in self.exchange_info["symbols"]:
            if s["symbol"] == self.symbol:
                for f in s["filters"]:
                    if f["filterType"] == "LOT_SIZE":
                        lot_size_filter = f
        return lot_size_filter

    def get_notional_filter(self):
        """
        Get MIN_NOTIONAL filter from exchange info:
        {
            "filterType": "MIN_NOTIONAL",
            "minNotional": "10.00000000",
            "applyToMarket": true,
            "avgPriceMins": 5
        }
        """
        notional_filter = None
        for s in self.exchange_info["symbols"]:
            if s["symbol"] == self.symbol:
                for f in s["filters"]:
                    if f["filterType"] == "NOTIONAL":
                        notional_filter = f
        return notional_filter

    def calc_min_qty(self, ticker_price):
        """
        Calculate min quantity based on minNotional and last price.
        """
        last_price = Decimal(ticker_price)
        min_notional = Decimal(self.get_notional_filter()["minNotional"])
        market_min_qty = min_notional / last_price

        filter = self.get_lot_size_filter()

        step_size_num = filter["stepSize"][1::].find("1")
        step_sized_min_qty = round_up(market_min_qty, step_size_num)

        filter_min_qty = Decimal(filter["minQty"])
        filter_max_qty = Decimal(filter["maxQty"])

        return Decimal(
            self._clamp_quantity(step_sized_min_qty, filter_min_qty, filter_max_qty)
        )
