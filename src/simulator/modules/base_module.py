"""base_module.py - Abstract base class for simulator modules
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from abc import ABC
from simulator.common.logger import logger


@dataclass
class BaseModuleState:
    """Class to hold the state of a module."""

    pass


class BaseModule(ABC):
    """Abstract base class for all simulator modules."""

    def __init__(self, name: str, state=BaseModuleState()) -> None:
        self.name = name
        self._state = state
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the module."""
        logger.debug(f"Initializing module: {self.name}")
