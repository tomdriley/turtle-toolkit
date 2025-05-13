"""cli.py - Set up command line arg parser for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import argparse
from importlib.metadata import metadata

from turtle_toolkit.common.logger import configure_logger

PROJECT_METADATA = metadata("turtle_toolkit")
PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=PROJECT_DESCRIPTION)

    # Command line arguments
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    # Create subparsers for the different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Assembler command
    assemble_parser = subparsers.add_parser(
        "assemble", help="Assemble source code to binary"
    )
    assemble_parser.add_argument("input_file", type=str, help="Assembly source file")
    assemble_parser.add_argument(
        "-o", "--output", type=str, help="Output binary file (default: input_file.bin)"
    )

    # Simulator command
    simulate_parser = subparsers.add_parser("simulate", help="Simulate binary code")
    simulate_parser.add_argument("input_file", type=str, help="Binary file to simulate")
    simulate_parser.add_argument(
        "-m",
        "--max-cycles",
        type=int,
        default=10000,
        help="Maximum number of cycles to simulate (default: 10000)",
    )

    # Combined command (assemble and simulate)
    combined_parser = subparsers.add_parser(
        "run", help="Assemble and simulate in one step"
    )
    combined_parser.add_argument("input_file", type=str, help="Assembly source file")
    combined_parser.add_argument(
        "-o", "--output", type=str, help="Intermediate binary file (optional)"
    )
    combined_parser.add_argument(
        "-m",
        "--max-cycles",
        type=int,
        default=10000,
        help="Maximum number of cycles to simulate (default: 10000)",
    )

    return parser.parse_args()


def setup_cli() -> argparse.Namespace:
    args = parse_args()
    configure_logger(args.verbose)
    return args
