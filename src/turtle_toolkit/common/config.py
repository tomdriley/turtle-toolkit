"""config.py - Loader/API for configurations
Author: Tom Riley
Date: 2025-05-04
"""

import yaml
from turtle_toolkit.common.singleton_meta import SingletonMeta
from typing import TypeVar, Type
from os import path

LOCAL_DIR = path.dirname(path.abspath(__file__))
CONFIG_FILE = path.join(LOCAL_DIR, "config.yml")

ConfigValue = TypeVar("ConfigValue", str, int, float, bool)


class Config(metaclass=SingletonMeta):
    """Singleton class to load and provide access to configuration settings."""

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self) -> dict:
        """Load the configuration file."""
        with open(self.config_file, "r") as file:
            return yaml.safe_load(file)

    def get(self, key: str, T: Type[ConfigValue]) -> ConfigValue:
        """Get a configuration value by key."""
        value = self.config_data.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found in configuration.")
        if not isinstance(value, T):
            raise TypeError(
                f"Expected type {str(T)} for key '{key}', "
                f"but got {str(type(value))}."
            )
        return value


DATA_WIDTH: int = Config(CONFIG_FILE).get("data_width", int)
INSTRUCTION_WIDTH: int = Config(CONFIG_FILE).get("instruction_width", int)
DATA_ADDRESS_WIDTH: int = Config(CONFIG_FILE).get("data_address_width", int)
INSTRUCTION_ADDRESS_WIDTH: int = Config(CONFIG_FILE).get(
    "instruction_address_width", int
)
