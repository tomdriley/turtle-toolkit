"""main.py - Main entry point for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.common.cli import setup_cli
from simulator.simulator import Simulator

if __name__ == "__main__":
    _ = setup_cli()
    simulutor = Simulator()
