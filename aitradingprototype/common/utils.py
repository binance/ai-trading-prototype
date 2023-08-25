import logging
import math
import re
import time
import uuid
from decimal import Decimal

import yaml


def load_config(file_path: str) -> dict:
    """
    Load config file and return the content as a dictionary.
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def config_logging(logging_level, log_file: str = None):
    """
    Configures logging to provide a more detailed log format, which includes date time in UTC
    Example: 2021-11-02 19:42:04.849 UTC <logging_level> <log_name>: <log_message>

    Args:
        logging_level (int/str): For logging to include all messages with log levels >= logging_level. Ex: 10 or "DEBUG"
                                 log levels reference - https://docs.python.org/3/library/logging.html#logging-levels
    Keyword Args:
        log_file (str, optional): The filename to pass the logging to a file, instead of using console. Default filemode: "a"
    """
    logging.Formatter.converter = time.gmtime  # date time in GMT/UTC
    logging.basicConfig(
        level=logging_level,
        filename=log_file,
        format="%(asctime)s.%(msecs)03d UTC %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def round_up(n, decimals=0):
    """
    Round up a given number n to the specified number of decimal places decimals.
    """
    multiplier = Decimal(10**decimals)
    return Decimal(math.ceil(n * multiplier)) / multiplier


def build_uuid():
    """
    Generate a UUID (Universally Unique Identifier) and return it as a string.
    """
    return str(uuid.uuid4())


def split_line(line):
    """
    Splits a line based on ',(?=")', this means, splits at ',' when it's followed by a '"'.
    Returns the list of splited elements, without the '"' enclosing the elements.
    """
    raw_elements = re.split(r',(?=")', line)
    elements = []
    for e in raw_elements:
        if e[0] == '"' and e[-1] == '"':
            elements.append(e[1:-1])
        else:
            elements.append(e)
    return elements
