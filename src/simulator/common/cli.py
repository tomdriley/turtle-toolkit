"""cli.py - Set up command line arg parser for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import argparse
from typing import Optional
from simulator.common.logger import logger, DEBUG, INFO

PROJECT_NAME = "Simulator"
PROJECT_VERSION = "0.1.0"
PROJECT_DESCRIPTION = "A cycle simulator for the TTL CPU ISA."


def _configure_logger(args: argparse.Namespace) -> None:
    """Configure the logger based on command line arguments."""
    if args.verbose:
        logger.setLevel(DEBUG)
        logger.debug("Verbose mode enabled.")
    else:
        logger.setLevel(INFO)

    logger.info(f"{PROJECT_NAME} v{PROJECT_VERSION} - {PROJECT_DESCRIPTION}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=PROJECT_DESCRIPTION)
    parser.add_argument("input_string", help="The string to process.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    parser.add_argument(
        "-o", "--output-file", type=str, help="Optional output file path."
    )
    return parser.parse_args()


def setup_cli() -> argparse.Namespace:
    args = _parse_args()
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
