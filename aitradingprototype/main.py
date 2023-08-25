import argparse
import logging
import sys

from aitradingprototype.common.utils import config_logging, load_config
from aitradingprototype.sg import SentimentGenerator
from aitradingprototype.tb import TradingBot

logger = logging.getLogger(__name__)


def _cmd_args():
    parser = argparse.ArgumentParser(
        prog="aitradingprototype",
        description="Free open source AI trading bot prototype",
    )

    # Create a mutually exclusive group for sg and tb options
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-sg",
        "--sentiment_generator",
        action="store_true",
        help="starts the sentiment generator process",
    )
    group.add_argument(
        "-tb",
        "--trading_bot",
        action="store_true",
        help="starts the trading bot process",
    )

    parser.add_argument(
        "config_file",
        type=str,
        help=".YAML config file for sentiment_generator or trading_bot process",
    )

    return parser.parse_args()


def main() -> None:
    """
    This function will initiate the trading bot.
    :return: None
    """
    return_code = 1
    try:
        args = _cmd_args()

        config_file = load_config(args.config_file)

        logging_level = config_file["logging_level"] or logging.INFO
        config_logging(logging_level)

        if args.sentiment_generator:
            SentimentGenerator(config_file).start()
        elif args.trading_bot:
            TradingBot(config_file).start()
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
        return_code = 0
    except Exception as e:
        logger.exception(e)
    finally:
        sys.exit(return_code)


if __name__ == "__main__":
    main()
