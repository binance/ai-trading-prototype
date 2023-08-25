import json
import logging

import redis

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Class for Redis operations
    """

    def __init__(self, host, port, channel: str):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.channel = channel

    def exists_key(self, key):
        """
        Check if key exists in Redis
        """
        return self.client.exists(key)

    def get_float_key(self, key):
        """
        Get value from Redis by key, if key does not exist yet, create and set it to 0
        """
        if not self.exists_key(key):
            self.set_key(key, 0)
        return float(self.client.get(key))

    def set_key(self, key, value: float):
        """
        Set key-value pair in Redis
        """
        self.client.set(key, value)
        logger.debug(f"New Redis {key}: {value}")

    def increment_key(self, key, quantity: float):
        """
        Increment key's value by quantity in Redis

        This increment option doesn't add extra digits due to IEEE 754 as ithappens (https://redis.io/commands/incrbyfloat).
        """
        existing_quantity = self.get_float_key(key)
        new_quantity = existing_quantity + quantity

        self.set_key(key, new_quantity)

    def decrement_key(self, key, quantity: float):
        """
        Decrement key's value by quantity in Redis"""
        existing_quantity = self.get_float_key(key)
        new_quantity = existing_quantity - quantity

        self.set_key(key, new_quantity)

    def publish_event(
        self,
        event_id: str,
        event_time: int,
        collected_source: str,
        collected_time: int,
        published_time: int,
        headline: str,
        sentiment: str,
    ):
        """
        Push headline sentiment event by using redis.publish for publish-subscribe messaging in Redis.
        It publishes a message to a specific channel in a "fire-and-forget" manner and any subscribers to that channel will receive the message.
        """

        event_data = {
            "event_id": event_id,
            "event_time": event_time,
            "collected_source": collected_source,
            "collected_time": collected_time,
            "published_time": published_time,
            "headline": headline,
            "sentiment": sentiment,
        }
        json_data = json.dumps(event_data)
        logger.info(f"Push event '{json_data}'")
        self.client.publish(self.channel, json_data)

    def listen_for_events(self, event_handler):
        # Subscribe to events channel
        pubsub = self.client.pubsub()
        pubsub.subscribe(self.channel)

        # Listen for new events
        for event in pubsub.listen():
            event_handler(event)
