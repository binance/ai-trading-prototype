from unittest.mock import MagicMock, patch

import pytest

from aitradingprototype.tb.trading_bot import TradingBot


@pytest.fixture
def mock_tb_config():
    """
    Generate a mock trading bot config for tests to reference
    """
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_channel": "headlines_sentiment",
        "base_url": "https://testnet.binance.vision",
        "trading_strategy": {
            "name": "successive",
            "symbol": "BTCUSDT",
            "base_asset": "BTC",
            "order_quantity": 0.001,
            "total_quantity_limit": 0.01,
        },
        "api_key": "123123123",
        "secret_key": "123123123",
        "private_key_path": "",
        "private_key_password": "",
        "input_option": "redis",
        "sentiments_file": "output/sentiments_btc.csv",
    }


def test_tb_init(mock_tb_config):
    """
    Initialise Trading Bot with mock clients for RedisClient, BinanceClient and SuccessiveStrategy
    """
    with patch(
        "aitradingprototype.tb.trading_bot.RedisClient"
    ) as MockRedisClient, patch(
        "aitradingprototype.tb.trading_bot.BinanceClient"
    ) as MockBinanceClient, patch(
        "aitradingprototype.tb.trading_bot.SuccessiveStrategy"
    ) as MockSuccessiveStrategy, patch(
        "aitradingprototype.tb.trading_bot.StrategyExecutor"
    ) as MockStrategyExecutor:
        tb = TradingBot(mock_tb_config)
        MockRedisClient.assert_called_once_with(
            mock_tb_config["redis_host"],
            mock_tb_config["redis_port"],
            mock_tb_config["redis_channel"],
        )
        MockBinanceClient.assert_called_once_with(
            base_url=mock_tb_config["base_url"],
            trading_strategy_config=mock_tb_config["trading_strategy"],
            api_key=mock_tb_config["api_key"],
            secret_key=mock_tb_config["secret_key"],
            private_key_path=mock_tb_config["private_key_path"],
            private_key_password=mock_tb_config["private_key_password"],
        )
        MockSuccessiveStrategy.assert_called_once_with(
            mock_tb_config["trading_strategy"]
        )
        MockStrategyExecutor.assert_called_once_with(
            tb.binance,
            tb.redis,
            f"aitp_{MockSuccessiveStrategy.return_value.__class__.__name__.lower()}_holding_qty_{mock_tb_config['trading_strategy']['base_asset'].lower()}",
        )


def test_tb_trade_based_on_redis(mock_tb_config):
    tb = TradingBot(mock_tb_config)
    tb.redis = MagicMock()
    tb.trade_based_on_redis()
    # Verify that tb.redis.listen_for_events is called with tb._event_handler
    tb.redis.listen_for_events.assert_called_once_with(tb._event_handler)
