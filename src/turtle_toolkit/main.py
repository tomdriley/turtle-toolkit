#!/usr/bin/env python3
"""main.py - Main entry point for TTL CPU Simulator and Assembler
Author: Tom Riley
Date: 2025-05-12

This module provides a comprehensive CLI interface for:
1. Assembling TTL CPU assembly code to binary
2. Simulating binary code on the TTL CPU simulator
3. Doing both in one step (assemble then simulate)
"""

import os
import sys
from importlib.metadata import metadata
from typing import Optional

from turtle_toolkit.assembler import Assembler
from turtle_toolkit.common.cli import setup_cli
from turtle_toolkit.common.logger import logger
from turtle_toolkit.simulator import Simulator

PROJECT_METADATA = metadata("turtle_toolkit")

PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


def read_text_file(file_path: str) -> str:
    """Read text from a file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def read_binary_file(file_path: str, allow_non_bin_ext: bool = False) -> bytes:
    """Read binary data from a file."""
    if not allow_non_bin_ext and not file_path.endswith(".bin"):
        logger.error(
            f"File {file_path} does not have a .bin extension. Did you mean to use 'run'? Use --allow-non-bin-ext to override."
        )
        sys.exit(1)
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

    result = simulator.run_until_halt(max_cycles)
    logger.info(f"Simulation completed in {result.cycle_count} cycles")

    # Print final state summary using our improved formatting
    print("\nSimulation Results:")
    print(f"Total cycles: {result.cycle_count}")
    print(f"Halted: {result.state.halted}")

    # Print a nicely formatted state summary
    print("\n" + simulator.format_simulator_state())


def main() -> None:
    """Main entry point for the application."""
    args = setup_cli()

    if not args.command:
        logger.error("No command specified. Use --help for usage information.")
        sys.exit(1)

    if args.command == "assemble":
        assemble_file(args.input_file, args.output)

    elif args.command == "simulate":
        binary = read_binary_file(args.input_file, args.allow_non_bin_ext)
        simulate_binary(binary, args.max_cycles)

    elif args.command == "run":
        # Assemble and then simulate
        binary = assemble_file(args.input_file, args.output)
        simulate_binary(binary, args.max_cycles)
