"""main.py - Main entry point for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.logger import logger
from simulator.cli import setup_cli
from simulator.add import add

if __name__ == "__main__":
    _ = setup_cli()
    a = 5
    b = 10
    result = add(a, b)
    logger.info(f"The sum of {a} and {b} is {result}.")
    logger.info("Hello, World!")
