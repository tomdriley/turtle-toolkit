"""logger.py - Set up logging for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import logging
import sys
from importlib.metadata import metadata

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING

PROJECT_METADATA = metadata("turtle_toolkit")

PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


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


def configure_logger(verbose: bool = False) -> None:
    """Configure the logger based on command line arguments."""
    if verbose:
        logger.setLevel(DEBUG)
        logger.debug("Verbose mode enabled.")
    else:
        logger.setLevel(INFO)

    logger.info(f"{PROJECT_NAME} v{PROJECT_VERSION}")
    logger.info(PROJECT_DESCRIPTION)


if __name__ == "__main__":
    log = _setup_logger("example_app")
    log.info("This is an info message.")
    log.error("This is an error message.")
