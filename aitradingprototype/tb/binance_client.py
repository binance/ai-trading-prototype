import logging
import os
import sys

from binance.error import ClientError
from binance.spot import Spot as Client

from aitradingprototype.__init__ import __version__
from aitradingprototype.tb.enums import TradingError
from aitradingprototype.tb.filter_manager import FilterManager

logger = logging.getLogger(__name__)


class BinanceClient:
    """
    Binance Client
    --------------
    Class to manage trading on Binance exchange
    """

    def __init__(
        self,
        base_url,
        trading_strategy_config,
        api_key,
        secret_key,
        private_key_path="",
        private_key_password="",
    ):
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, "rb") as f:
                private_key = f.read()
            self.client = Client(
                api_key=api_key,
                private_key=private_key,
                private_key_pass=private_key_password,
                base_url=base_url,
            )
        elif secret_key:
            self.client = Client(api_key, secret_key, base_url=base_url)
        else:
            logger.error(
                "Either private key or secret key must be set in the Trading Bot's config YAML."
            )
            sys.exit(1)

        self.client.session.headers.update(
            {"User-Agent": "ai-trading-prototype/" + __version__}
        )
        self.symbol = trading_strategy_config["symbol"]
        self.base_asset = trading_strategy_config["base_asset"]
        self.fm = None

    def get_filter_manager(self):
        """
        Get filter manager
        """
        if not self.fm:
            self.fm = FilterManager(self.symbol, self.client.exchange_info())

        return self.fm

    def post_order(self, args):
        """
        Post order to Binance
        """
        try:
            logger.info(f"Post order '{args}'")
            return self.client.new_order(**args)

        except ClientError as error:
            if (
                error.error_code == -1013
                and error.error_message == "Filter failure: NOTIONAL"
            ):
                ticker_price = (self.client.ticker_price(self.symbol))["price"]
                min_qty = self.get_filter_manager().calc_min_qty(ticker_price)
                logger.error((TradingError.NOTIONAL_FILTER.value).format(min_qty))
            else:
                logger.error(error)
                sys.exit(1)
