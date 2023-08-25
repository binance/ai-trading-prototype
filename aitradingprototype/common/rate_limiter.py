import logging
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter class to control API call limits
    """

    def __init__(self, max_calls: int, interval: int):
        self.max_calls = max_calls
        self.interval = interval  # seconds
        self.calls_made = 0
        self.last_call_time = 0

    def rate_limiter(self):
        """
        Rate limiter to prevent exceeding API call limits
        """
        current_time = time.time()

        if self.calls_made == self.max_calls:
            time_elapsed = current_time - self.last_call_time
            if time_elapsed < self.interval:
                sleep_time = (
                    self.interval - time_elapsed
                )  # wait time until UTC new minute
                logger.debug(f"Rate limit reached. Waiting {sleep_time} seconds.")
                time.sleep(sleep_time)
                self.calls_made = 0

        self.calls_made += 1
        self.last_call_time = time.time()
