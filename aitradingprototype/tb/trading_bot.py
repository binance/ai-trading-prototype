import json
import logging

from aitradingprototype.common import FileOperator, RedisClient
from aitradingprototype.common.enums import Sentiment
from aitradingprototype.common.utils import split_line
from aitradingprototype.tb import BinanceClient
from aitradingprototype.tb.enums import OrderAction
from aitradingprototype.tb.strategy import SuccessiveStrategy
from aitradingprototype.tb.strategy_executor import StrategyExecutor

logger = logging.getLogger(__name__)


class TradingBot:
    """
    Trading Bot
    -----------
    This class is responsible for the trading on Binance based on received sentiments and defined strategy.
    """

    def __init__(self, config: dict):
        self.config = config
        self.redis = self.redis = RedisClient(
            self.config["redis_host"],
            self.config["redis_port"],
            self.config["redis_channel"],
        )
        self.binance = BinanceClient(
            base_url=config["base_url"],
            trading_strategy_config=config["trading_strategy"],
            api_key=config["api_key"],
            secret_key=config["secret_key"],
            private_key_path=config["private_key_path"],
            private_key_password=config["private_key_password"],
        )
        self.strategy = SuccessiveStrategy(self.config["trading_strategy"])

        base_asset = config["trading_strategy"]["base_asset"]
        holding_qty_key = f"aitp_{self.strategy.__class__.__name__.lower()}_holding_qty_{base_asset.lower()}"
        self.strategy_executor = StrategyExecutor(
            self.binance, self.redis, holding_qty_key
        )

    def _process_sentimet(self, sentiment: str):
        """
        Process known sentiments and skip unknown ones.
        """
        if sentiment == Sentiment.UNKNOWN.value:
            logger.info(
                OrderAction.SKIP_ORDER.value.format(
                    f"sentiment is {Sentiment.UNKNOWN.value}"
                )
            )
        elif (
            sentiment == Sentiment.BULLISH.value or sentiment == Sentiment.BEARISH.value
        ):
            holding_quantity = self.strategy_executor.holding_qty()
            logger.info(
                f"Current {self.strategy_executor.holding_qty_key}: {holding_quantity}"
            )
            strategy_order = self.strategy.order_strategy(sentiment, holding_quantity)
            logger.debug(f"Strategy order specification: {strategy_order}")
            self.strategy_executor.execute_order(strategy_order)
        else:
            logger.warning(
                OrderAction.AVOID_ORDER.value.format(f"invalid sentiment {sentiment}"),
            )

    def _event_handler(self, event):
        """
        Handle different types of JSON events and processes them accordingly.
        If event type is `subscribe`, logs the sucessful subscription.
        If event type is `message`, processes the event message.
        Example of event:
        {
            'type': 'message',
            'pattern': None,
            'channel': 'headlines_sentiment',
            'data': '{
                "event_id": "afd049cb-b19c-4cba-be14-5ddbf3f1aea0",
                "event_time": 1692869093677,
                "collected_source": "NewsAPI",
                "collected_time": 1686376494108,
                "published_time": 1685376494108,
                "headline": "headline",
                "sentiment": "bullish"
            }'
        }
        """
        logger.info(f"Received event '{event}'")
        if event["type"] == "subscribe":
            logger.info(f"Subscribed to channel '{self.config['redis_channel']}'")
        elif event["type"] == "message":
            event_data = event["data"]
            sentiment = (json.loads(event_data))["sentiment"]
            self._process_sentimet(sentiment)
        else:
            logger.warning(f"Unknown event type '{event['type']}'")

    def trade_based_on_file(self):
        """
        Read sentiments from file and trades based on them
        """
        input_file = self.config["sentiments_file"]
        logger.info(f"Reading from file '{input_file }'...")
        file_operator = FileOperator(input_file, "r")

        for line in file_operator.follow_line():
            logger.info(f"Read '{line}'")
            sentiment = split_line(line)[-1]
            self._process_sentimet(sentiment)

    def trade_based_on_redis(self):
        """
        Listen for sentiments events from Redis and trades based on them
        """
        self.redis.listen_for_events(self._event_handler)

    def start(self):
        """
        Start trading
        """
        logger.info("Start trading.")
        input_option = self.config["input_option"]
        if input_option == "file":
            self.trade_based_on_file()
        else:
            self.trade_based_on_redis()
