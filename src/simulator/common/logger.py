"""logger.py - Set up logging for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import logging
import sys

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING


def _setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Sets up a basic logger."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


logger = _setup_logger(__name__)

if __name__ == "__main__":
    log = _setup_logger("example_app")
    log.info("This is an info message.")
    log.error("This is an error message.")
