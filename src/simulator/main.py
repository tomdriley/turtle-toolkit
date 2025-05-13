#!/usr/bin/env python3
"""main.py - Main entry point for TTL CPU Simulator and Assembler
Author: Tom Riley
Date: 2025-05-12

This module provides a comprehensive CLI interface for:
1. Assembling TTL CPU assembly code to binary
2. Simulating binary code on the TTL CPU simulator
3. Doing both in one step (assemble then simulate)
"""

import argparse
import os
import sys
from typing import Optional
from importlib.metadata import metadata

from simulator.common.logger import logger, configure_logger
from simulator.assembler import Assembler
from simulator.simulator import Simulator

PROJECT_METADATA = metadata("simulator")

PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


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


def read_text_file(file_path: str) -> str:
    """Read text from a file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def read_binary_file(file_path: str) -> bytes:
    """Read binary data from a file."""
    try:
        with open(file_path, "rb") as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def write_binary_file(file_path: str, data: bytes) -> None:
    """Write binary data to a file."""
    try:
        with open(file_path, "wb") as file:
            file.write(data)
        logger.info(f"Binary written to: {file_path}")
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        sys.exit(1)


def assemble_file(input_file: str, output_file: Optional[str] = None) -> bytes:
    """Assemble the input file and save to output file if specified."""
    if not output_file:
        # Default output file is input_file with .bin extension
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.bin"

    logger.info(f"Assembling {input_file} to {output_file}")

    source_code = read_text_file(input_file)
    try:
        binary = Assembler.assemble(source_code)
        write_binary_file(output_file, binary)
        logger.info(f"Assembly successful: {len(binary)//2} instructions written")
        return binary
    except Exception as e:
        logger.error(f"Assembly failed: {e}")
        sys.exit(1)


def simulate_binary(binary: bytes, max_cycles: int = 10000) -> None:
    """Simulate the binary code."""
    logger.info(f"Simulating binary code ({len(binary)//2} instructions)")

    simulator = Simulator()
    simulator.reset()
    simulator.load_binary(binary)

    try:
        result = simulator.run_until_halt(max_cycles)
        logger.info(f"Simulation completed in {result.cycle_count} cycles")

        # Print final state summary
        print("\nSimulation Results:")
        print(f"Total cycles: {result.cycle_count}")
        print(f"Halted: {result.state.halted}")
        print("Final register values:")
        reg_file = simulator._register_file
        print(f"  ACC: {reg_file.get_acc_value()}")
        print(f"  Status: {reg_file.get_status_register_value()}")

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    args = parse_args()

    if not args.command:
        logger.error("No command specified. Use --help for usage information.")
        sys.exit(1)

    configure_logger(args.verbose)

    if args.command == "assemble":
        assemble_file(args.input_file, args.output)

    elif args.command == "simulate":
        binary = read_binary_file(args.input_file)
        simulate_binary(binary, args.max_cycles)

    elif args.command == "run":
        # Assemble and then simulate
        binary = assemble_file(args.input_file, args.output)
        simulate_binary(binary, args.max_cycles)
