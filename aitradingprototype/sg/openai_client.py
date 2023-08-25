import logging

import openai

from aitradingprototype.common import RateLimiter
from aitradingprototype.common.enums import Sentiment

logger = logging.getLogger(__name__)


class OpenAiClient:
    """
    OpenAI Client
    -------------
    This class interacts with OpenAI API to generate market sentiment based on the given headline.
    """

    def __init__(
        self, api_key: str, num_requests: int = 3, openai_model: str = "gpt-3.5-turbo"
    ):
        openai.api_key = api_key

        self.min_rate_limiter = RateLimiter(num_requests, 60)
        self.openai_model = openai_model

    def _optimize_accuracy(self, result):
        """
        Optimize the sentiment result: no period(.) and in lowercases
        """
        return result.replace(".", "").lower()

    def detect_sentiment(self, headline: str, asset: str):
        """
        Given 'headline', this method uses OpenAI's API to generate one word market sentiment about 'asset' cryptocurrency.
        Returns sentiment as string.

        OpenAI API endpoint: https://platform.openai.com/docs/api-reference/chat-completions/create
        Endpoint parameters are set with default values to improve the result accuracy.
        For more information about the parameters, please refer to https://platform.openai.com/docs/api-reference/chat/create
        """

        system_content = (
            f"You are a contextual sentiment indicator that replies:"
            f"\n- only one word ('{Sentiment.BULLISH.value}', '{Sentiment.BEARISH.value}', or '{Sentiment.UNKNOWN.value}')"
            f"\n- without punctuation"
            f"\n- in lowercases"
        )
        system_role_msg = {"role": "system", "content": system_content}

        user_content = f'For this "{headline}", generate sentiment about "{asset}"'
        user_role_msg = {"role": "user", "content": user_content}

        response = openai.ChatCompletion.create(
            messages=[system_role_msg, user_role_msg],
            model=self.openai_model,
            temperature=0,  # no randomness
            max_tokens=2,  # sentiment word has max 2 tokens
            n=1,  # number of chat completion choices
        )
        logger.debug(f"OpenAI response: {response}")
        return self._optimize_accuracy(response["choices"][0]["message"]["content"])

    def request_sentiment(self, headline: str, asset: str):
        """
        Rate limit the market sentiment API call and return the sentiment
        """
        self.min_rate_limiter.rate_limiter()
        return self.detect_sentiment(headline, asset)
