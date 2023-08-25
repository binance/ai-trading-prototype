from unittest.mock import MagicMock, patch

import pytest

from aitradingprototype.sg import SentimentGenerator


@pytest.fixture
def sample_config():
    """
    Generate a sentiment generator config for tests to reference
    """
    return {
        "asset": "BTC",
        "headlines_file": "headlines/headlines_sample.csv",
        "output_option": "file",
        "openai_api_key": "MOCK_OPENAI_API_KEY",
        "reqs_min": 3,
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_channel": "headlines_sentiment",
        "logging_level": "INFO",
    }


@pytest.fixture
def headline_file_line():
    """
    Generate a sample headline file line
    """
    return '"Source","1697262400000","1687262400000","headline"'


def test_sentiment_generator_init(sample_config):
    sg = SentimentGenerator(sample_config)
    assert sg is not None


def test_create_sentiment_line_with_valid_headline_line(
    sample_config, headline_file_line
):
    config = sample_config
    sg = SentimentGenerator(config)

    # Create a mock openaiclient instance
    mock_openai_client = MagicMock()
    mock_openai_client.request_sentiment.return_value = "bullish"

    # Set the openai attribute to the mock instance
    sg.openai = mock_openai_client

    sentiment_line = sg._create_sentiment_line(headline_file_line)
    assert (
        sentiment_line
        == '"Source","1697262400000","1687262400000","headline","bullish"'
    )


def test_create_sentiment_line_with_invalid_headline_line(sample_config):
    config = sample_config
    sg = SentimentGenerator(config)

    # Create a mock openaiclient instance
    mock_openai_client = MagicMock()
    mock_openai_client.request_sentiment.return_value = "bullish"

    # Set the openai attribute to the mock instance
    sg.openai = mock_openai_client

    with pytest.raises(ValueError):
        headline = (
            "abc"  # Invalid headline, no comma between published time and headline
        )
        sg._create_sentiment_line(headline)


def test_write_file(sample_config, headline_file_line):
    config = sample_config
    sg = SentimentGenerator(config)

    # Mock the headlines_file_operator to return sample headlines
    mock_headlines_file_operator = MagicMock()
    mock_headlines_file_operator.follow_line.return_value = [
        headline_file_line,
        headline_file_line,
    ]
    sg.headlines_file_operator = mock_headlines_file_operator

    # Mock openai_client to return a predefined sentiment
    mock_openai_client = MagicMock()
    mock_openai_client.request_sentiment.return_value = "bullish"
    sg.openai = mock_openai_client

    # Mock output file path to avoid real file writing
    mock_write_file_path = MagicMock()
    sg._create_sentiments_output_file_path = mock_write_file_path

    sg.write_file()


def test_push_redis(sample_config, headline_file_line):
    config = sample_config
    sg = SentimentGenerator(config)

    # Mock the headlines_file_operator to return sample headlines
    mock_headlines_file_operator = MagicMock()
    mock_headlines_file_operator.follow_line.return_value = [
        headline_file_line,
        headline_file_line,
    ]
    sg.headlines_file_operator = mock_headlines_file_operator

    # Mock openai_client to return a predefined sentiment
    mock_openai_client = MagicMock()
    mock_openai_client.request_sentiment.return_value = "bullish"
    sg.openai = mock_openai_client

    # Mock redis client to avoid real redis connection
    mock_redis_client = MagicMock()
    sg.redis = mock_redis_client

    # Call the push_redis method
    sg.push_redis()
