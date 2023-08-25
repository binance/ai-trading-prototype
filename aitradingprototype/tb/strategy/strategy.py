from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    Strategy
    --------
    Base class to define trading strategy
    """

    def __init__(self, trading_spec: dict):
        self.trading_spec = trading_spec  # trading_spec is a dictionary that contains the following keys for the trading strategy

    @abstractmethod
    def order_strategy(self, *args):
        """
        Provides a trading strategy
        """
        pass
