import logging
import os
import time

from aitradingprototype.common import FileOperator, RedisClient
from aitradingprototype.common.utils import build_uuid, split_line
from aitradingprototype.sg import OpenAiClient

logger = logging.getLogger(__name__)


class SentimentGenerator:
    """
    Sentiment Generator
    -------------------
    Generates headlines sentiment based on the headlines file, and writes the sentiment to a file or pushes it to redis.

    Generated sentiment file line format:
    ```
    "headline collected source","headline collected timestamp (ms)","headline published timestamp (ms)","headline","sentiment"
    "NewsAPI","1686376494108","1685376494108","headline","bullish"
    ```

    Generated sentiment event format:
    ```json
        {
            "event_id": "afd049cb-b19c-4cba-be14-5ddbf3f1aea0",
            "event_time": 1692869093677,
            "collected_source": "NewsAPI",
            "collected_time": 1686376494108,
            "published_time": 1685376494108,
            "headline": "headline",
            "sentiment": "bullish"
        }
    ```
    """

    def __init__(self, config: dict):
        self.config = config
        self.headlines_file_operator = FileOperator(config["headlines_file"], "r")
        self.openai = OpenAiClient(
            self.config["openai_api_key"], self.config["reqs_min"]
        )
        self.redis = None

    def _create_sentiment_line(self, line):
        """
        Process each line from headlines file and generate sentiment based on the headline
        """
        source, collected_time, published_time, headline = split_line(line)
        sentiment = self.openai.request_sentiment(headline, self.config["asset"])
        return f'"{source}","{collected_time}","{published_time}","{headline}","{sentiment}"'

    def _create_sentiments_output_file_path(self):
        """
        Create a './output/sentiments_<asset>.csv' if it doesn't exist already
        """
        asset = self.config["asset"].lower()
        output_directory = "./output/"
        output_file = f"sentiments_{asset}.csv"

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        return os.path.join(output_directory, output_file)

    def write_file(self):
        """
        Write headlines with sentiments to a file
        """
        output_file_path = self._create_sentiments_output_file_path()
        file_operator = FileOperator(output_file_path, "w+")
        logger.info(f"Writing to '{output_file_path}'...")
        for line in self.headlines_file_operator.follow_line():
            logger.debug(f"Read '{line}'")
            sentiment_line = self._create_sentiment_line(line)
            logger.info(f"Write '{sentiment_line}'")
            file_operator.write_line(sentiment_line + "\n")

    def push_redis(self):
        """
        Push headlines with sentiments to redis
        """
        for line in self.headlines_file_operator.follow_line():
            sentiment_line = self._create_sentiment_line(line)
            (
                collected_source,
                collected_time,
                published_time,
                headline,
                sentiment,
            ) = split_line(sentiment_line)
            event_push_time = int(time.time() * 1000)

            if self.redis is None:
                self.redis = RedisClient(
                    self.config["redis_host"],
                    self.config["redis_port"],
                    self.config["redis_channel"],
                )
            self.redis.publish_event(
                build_uuid(),
                event_push_time,
                collected_source,
                int(collected_time),
                int(published_time),
                headline,
                sentiment,
            )

    def start(self):
        """
        Start sentiment generator
        """

        logger.info("Start sentiment generator")
        logger.info(f"Reading from file '{self.headlines_file_operator.file_name}'...")
        output_option = self.config["output_option"]
        if output_option == "file":
            self.write_file()
        else:
            self.push_redis()
