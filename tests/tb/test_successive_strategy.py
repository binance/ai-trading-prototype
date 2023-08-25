from aitradingprototype.common.enums import Sentiment
from aitradingprototype.tb.enums import OrderAction
from aitradingprototype.tb.strategy.successive_strategy import SuccessiveStrategy

# test order_strategy function


def create_trading_spec(symbol, base_asset, quantity, total_quantity_limit):
    return {
        "symbol": symbol,
        "base_asset": base_asset,
        "order_quantity": quantity,
        "total_quantity_limit": total_quantity_limit,
    }


def test_buy_with_exceeding_total_quantity_limit():
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=0.5
    )
    order_strategy = SuccessiveStrategy(trading_spec)
    assert (
        order_strategy.order_strategy(
            sentiment="bullish",
            holding_quantity=0,
        )["action"]
        == OrderAction.SKIP_ORDER
    )


def test_sell_without_holding_quantity():
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=0.5
    )
    order_strategy = SuccessiveStrategy(trading_spec)
    assert (
        order_strategy.order_strategy(
            sentiment="bearish",
            holding_quantity=0,
        )["action"]
        == OrderAction.SKIP_ORDER
    )


def test_bullish_in_row_without_exceeding_total_quantity_limit():
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=3
    )
    order_strategy = SuccessiveStrategy(trading_spec)

    assert (
        order_strategy.order_strategy(
            sentiment="bullish",
            holding_quantity=0,
        )["action"]
        == OrderAction.POST_ORDER
    )
    net_quantity_after_buy = 1
    assert (
        order_strategy.order_strategy(
            sentiment="bullish",
            holding_quantity=net_quantity_after_buy,
        )["action"]
        == OrderAction.POST_ORDER
    )


def test_bearish_in_row_with_enough_holding_quantity():
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=3
    )
    order_strategy = SuccessiveStrategy(trading_spec)

    assert (
        order_strategy.order_strategy(
            sentiment="bearish",
            holding_quantity=3,
        )["action"]
        == OrderAction.POST_ORDER
    )
    quantity_after_sell = 2
    assert (
        order_strategy.order_strategy(
            sentiment="bearish",
            holding_quantity=quantity_after_sell,
        )["action"]
        == OrderAction.POST_ORDER
    )


def test_order_alternations_with_bullish_start():
    """
    Start with bullish sentiment, then alternate between bullish and bearish.
    Starts with holding_quantity = 0
    """
    sentiments = ["bullish", "bearish", "bullish", "bearish"]
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=3
    )
    order_strategy = SuccessiveStrategy(trading_spec)

    net_quantity_after_buy = 1
    net_quantity_after_sell = 0
    for sentiment in sentiments:
        if sentiment == Sentiment.BULLISH.value:
            assert (
                order_strategy.order_strategy(
                    sentiment,
                    holding_quantity=net_quantity_after_sell,
                )["action"]
                == OrderAction.POST_ORDER
            )

        elif sentiment == Sentiment.BEARISH.value:
            strat = order_strategy.order_strategy(
                sentiment,
                holding_quantity=net_quantity_after_buy,
            )
            assert strat["action"] == OrderAction.POST_ORDER
            assert strat["order"]["quantity"] == net_quantity_after_buy


def test_order_alternations_with_bearish_start():
    """
    Starts with bearish sentiment, then alternate between bearish and bullish.
    Starts with holding_quantity = 1
    """
    sentiments = ["bearish", "bullish", "bearish", "bullish"]
    trading_spec = create_trading_spec(
        symbol="BTCUSDT", base_asset="BTC", quantity=1, total_quantity_limit=3
    )
    order_strategy = SuccessiveStrategy(trading_spec)

    net_quantity_after_buy = 1
    net_quantity_after_sell = 0
    for sentiment in sentiments:
        if sentiment == Sentiment.BEARISH.value:
            strat = order_strategy.order_strategy(
                sentiment,
                holding_quantity=net_quantity_after_buy,
            )
            assert strat["action"] == OrderAction.POST_ORDER
            assert strat["order"]["quantity"] == net_quantity_after_buy
        elif sentiment == Sentiment.BULLISH.value:
            assert (
                order_strategy.order_strategy(
                    sentiment,
                    holding_quantity=net_quantity_after_sell,
                )["action"]
                == OrderAction.POST_ORDER
            )
