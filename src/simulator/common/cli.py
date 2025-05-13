"""cli.py - Set up command line arg parser for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import argparse
from typing import Optional
from simulator.common.logger import logger, DEBUG, INFO
from importlib.metadata import metadata

PROJECT_METADATA = metadata("simulator")
PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


def _configure_logger(args: argparse.Namespace) -> None:
    """Configure the logger based on command line arguments."""
    if args.verbose:
        logger.setLevel(DEBUG)
        logger.debug("Verbose mode enabled.")
    else:
        logger.setLevel(INFO)

    logger.info(f"{PROJECT_NAME} v{PROJECT_VERSION} - {PROJECT_DESCRIPTION}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=PROJECT_DESCRIPTION)

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
    assemble_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
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
    simulate_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
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
    combined_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    return parser.parse_args()


def setup_cli() -> argparse.Namespace:
    args = parse_args()
    _configure_logger(args)
    return args


def _process_data(input_string: str) -> str:
    """Process the input string and return a result."""
    # Placeholder for actual processing logic
    logger.debug(f"Processing input: {input_string}")
    processed_string = input_string[::-1]  # Example: reverse the string
    logger.debug(f"Processed output: {processed_string}")
    return processed_string


def _main(
    input_string: str, verbose: bool = False, output_file: Optional[str] = None
) -> None:
    """Main function to process the input string."""

    logger.info(f"Received input: {input_string}")
    processed_output = _process_data(input_string)
    logger.info(f"Processed output: {processed_output}")

    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(processed_output + "\n")
            logger.info(f"Output written to: {output_file}")
        except IOError as e:
            logger.error(f"Error writing to file {output_file}: {e}")
    else:
        print(f"Output: {processed_output}")


if __name__ == "__main__":
    args = setup_cli()
    _main(args.input_string, args.verbose, args.output_file)
