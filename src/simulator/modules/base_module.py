"""base_module.py - Abstract base class for simulator modules
Author: Tom Riley
Date: 2025-05-04
"""

from abc import ABC
from simulator.common.logger import logger


class BaseModule(ABC):
    """Abstract base class for all simulator modules."""

    def __init__(self, name: str) -> None:
        self.name = name
        logger.debug(f"Initializing module: {self.name}")

    def initialize(self) -> None:
        """Initialize the module."""
        logger.debug(f"Initializing module: {self.name}")
        pass
