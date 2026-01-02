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
from turtle_toolkit.common.cli import AssemblerFormats, CommentLevel, setup_cli
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


def read_binary_string_file(file_path: str) -> bytes:
    """Read binary data from a binary string format file (.binstr.txt).

    Args:
        file_path: Path to the binary string file

    Returns:
        Binary data parsed from the file

    The format expected is any text file containing binary digits (0 and 1).
    Comments (// to end of line) and all whitespace are ignored.
    """
    if not (file_path.endswith(".binstr.txt") or file_path.endswith(".binstr")):
        logger.warning(f"File {file_path} does not have expected .binstr.txt extension")

    try:
        with open(file_path, "r") as file:
            content = file.read()
    except IOError as e:
        logger.error(f"Error reading binary string file {file_path}: {e}")
        sys.exit(1)

    # Remove all comments (// to end of line)
    lines = content.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove everything after // (including //)
        if "//" in line:
            line = line[: line.index("//")]
        cleaned_lines.append(line)

    # Join all lines and remove all whitespace
    binary_text = "".join(cleaned_lines)
    binary_text = "".join(binary_text.split())  # Remove all whitespace

    # Validate that we only have binary digits
    if not all(c in "01" for c in binary_text):
        invalid_chars = set(c for c in binary_text if c not in "01")
        logger.error(
            f"Invalid characters in binary string: {invalid_chars}. Only '0' and '1' are allowed."
        )
        sys.exit(1)

    if len(binary_text) == 0:
        logger.error(f"No binary data found in file {file_path}")
        sys.exit(1)

    # Ensure we have complete instructions (multiple of 8 bits)
    if len(binary_text) % 8 != 0:
        padding_needed = 8 - (len(binary_text) % 8)
        logger.warning(
            f"Binary string length ({len(binary_text)}) is not a multiple of 8. Adding {padding_needed} zero bits for padding."
        )
        binary_text += "0" * padding_needed

    # Convert binary string to bytes
    binary_data = bytearray()
    for i in range(0, len(binary_text), 8):
        byte_str = binary_text[i : i + 8]
        byte_value = int(byte_str, 2)
        binary_data.append(byte_value)

    # Ensure we have complete instructions (even number of bytes)
    if len(binary_data) % 2 != 0:
        logger.warning(
            f"Binary data length ({len(binary_data)}) is odd. Adding padding byte."
        )
        binary_data.append(0)

    logger.info(
        f"Parsed {len(binary_data)} bytes ({len(binary_data)//2} instructions) from binary string file"
    )
    return bytes(binary_data)


def write_binary_file(file_path: str, data: bytes) -> None:
    """Write binary data to a file."""
    try:
        with open(file_path, "wb") as file:
            file.write(data)
        logger.info(f"Binary written to: {file_path}")
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        sys.exit(1)


def write_text_file(file_path: str, data: str) -> None:
    """Write text data to a file."""
    try:
        with open(file_path, "w") as file:
            file.write(data)
        logger.info(f"Text written to: {file_path}")
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        sys.exit(1)


def assemble_file(
    input_file: str,
    output_file: Optional[str] = None,
    format: AssemblerFormats = AssemblerFormats.BIN,
    output_length: int = 0,
    comment_level: CommentLevel = CommentLevel.STRIPPED,
    binstr_byte_per_line: bool = False,
) -> bytes:
    """Assemble the input file and save to output file if specified."""
    if not output_file:
        # Default output file is input_file with .bin extension
        base_name = os.path.splitext(input_file)[0]
        extension = "bin" if format == AssemblerFormats.BIN else f"{format.value}.txt"
        output_file = f"{base_name}.{extension}"

    logger.info(f"Assembling {input_file} to {output_file}")

    source_code = read_text_file(input_file)
    try:
        # Assemble, then apply padding (so text formats can include the padded bytes too)
        if format == AssemblerFormats.BIN:
            binary = Assembler.assemble(source_code)
            instructions = None
            source_lines = None
        elif format == AssemblerFormats.BINARY_STRING:
            if comment_level == CommentLevel.FULL:
                binary, source_lines = Assembler.assemble_with_full_source_info(
                    source_code
                )
                instructions = None
            elif comment_level == CommentLevel.STRIPPED:
                binary, instructions = Assembler.assemble_with_source_info(source_code)
                source_lines = None
            else:  # NONE
                binary = Assembler.assemble(source_code)
                instructions = None
                source_lines = None
        elif format == AssemblerFormats.HEX_STRING:
            if comment_level == CommentLevel.FULL:
                binary, source_lines = Assembler.assemble_with_full_source_info(
                    source_code
                )
                instructions = None
            elif comment_level == CommentLevel.STRIPPED:
                binary, instructions = Assembler.assemble_with_source_info(source_code)
                source_lines = None
            else:  # NONE
                binary = Assembler.assemble(source_code)
                instructions = None
                source_lines = None
        else:
            raise ValueError(f"Unsupported format: {format}")

        binary_length = len(binary)

        if output_length > 0 and binary_length > output_length:
            raise ValueError(
                f"Output length {output_length} is less than the assembled binary length {binary_length}"
            )
        if output_length > 0 and binary_length < output_length:
            binary += b"\x00" * (output_length - binary_length)

        # Format output
        if format == AssemblerFormats.BIN:
            write_binary_file(output_file, binary)
        elif format == AssemblerFormats.BINARY_STRING:
            formatted_text = Assembler.format_binary_string(
                binary=binary,
                input_filename=input_file,
                comment_level=comment_level.value,
                instructions=instructions,
                source_lines=source_lines,
                one_byte_per_line=binstr_byte_per_line,
            )
            write_text_file(output_file, formatted_text)
        else:  # HEX_STRING
            formatted_text = Assembler.format_hex_string(
                binary=binary,
                input_filename=input_file,
                comment_level=comment_level.value,
                instructions=instructions,
                source_lines=source_lines,
            )
            write_text_file(output_file, formatted_text)

        logger.info(f"Assembly successful: {binary_length//2} instructions written")
        if output_length > binary_length:
            logger.info(f"Output padded to {output_length} bytes with zeroes")
        return binary
    except Exception as e:
        logger.error(f"Assembly failed: {e}")
        sys.exit(1)


def simulate_binary(
    binary: bytes,
    max_cycles: int = 10000,
    dump_memory: Optional[str] = None,
    dump_registers: Optional[str] = None,
    dump_memory_full: bool = False,
) -> None:
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

    # Dump state to files if requested
    if dump_memory:
        try:
            memory_content = simulator.get_data_memory_dump(dump_memory_full)
            write_text_file(dump_memory, memory_content)
            print(f"\nData memory state dumped to: {dump_memory}")
            if dump_memory_full:
                print("  (Full memory space included)")
        except Exception as e:
            logger.error(f"Failed to dump data memory state: {e}")

    if dump_registers:
        try:
            register_content = simulator.get_register_file_dump()
            write_text_file(dump_registers, register_content)
            print(f"Register file state dumped to: {dump_registers}")
        except Exception as e:
            logger.error(f"Failed to dump register file state: {e}")


def compare_memory_dumps(
    file1: str, file2: str, ignore_comments: bool = True, verbose: bool = False
) -> bool:
    """Compare two memory dump files, ignoring comments if specified.

    Returns:
        bool: True if files are identical, False if they differ or an error occurs.
    """
    logger.info(f"Comparing memory dumps: {file1} vs {file2}")

    try:
        content1 = read_text_file(file1)
        content2 = read_text_file(file2)
    except Exception as e:
        logger.error(f"Failed to read dump files: {e}")
        return False

    # Extract binary values from each file
    def extract_binary_values(content: str) -> list[str]:
        lines = content.strip().split("\n")
        binary_values = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue  # Skip empty lines and comment-only lines

            if ignore_comments:
                # Extract just the binary part (before any //)
                parts = line.split("//")
                binary_part = parts[0].strip()
            else:
                binary_part = line

            # Check if this looks like a binary string (only 0s, 1s, and whitespace)
            if binary_part and all(c in "01 \t" for c in binary_part):
                # Remove all whitespace for comparison
                clean_binary = "".join(binary_part.split())
                binary_values.append(clean_binary)

        return binary_values

    values1 = extract_binary_values(content1)
    values2 = extract_binary_values(content2)

    # Normalize arrays to handle trailing zeros - pad shorter array with zeros
    max_len = max(len(values1), len(values2))
    
    # Pad with zeros if needed
    while len(values1) < max_len:
        values1.append("00000000")  # 8-bit zeros
    while len(values2) < max_len:
        values2.append("00000000")  # 8-bit zeros

    # Compare the binary values (now they have equal length)
    mismatches = []
    for i, (val1, val2) in enumerate(zip(values1, values2)):
        if val1 != val2:
            mismatches.append((i, val1, val2))

    if not mismatches:
        print("✅ SUCCESS: Memory dumps are identical!")
        if verbose:
            print(f"  Compared {len(values1)} binary values")
            print(f"  File 1: {file1}")
            print(f"  File 2: {file2}")
        return True
    else:
        print(f"❌ MISMATCH: Found {len(mismatches)} differences")
        print(f"  Total values compared: {len(values1)}")

        if verbose:
            print("\nDetailed differences:")
            for index, val1, val2 in mismatches[:10]:  # Show first 10 mismatches
                print(f"  Index {index:3}: {val1} ≠ {val2}")
            if len(mismatches) > 10:
                print(f"  ... and {len(mismatches) - 10} more differences")
        else:
            print("  Use --verbose to see detailed differences")
        return False


def main() -> None:
    """Main entry point for the application."""
    args = setup_cli()

    if not args.command:
        logger.error("No command specified. Use --help for usage information.")
        sys.exit(1)

    if args.command == "assemble":
        assemble_file(
            args.input_file,
            args.output,
            args.format,
            args.output_length,
            args.comments,
            args.binstr_byte_per_line,
        )

    elif args.command == "simulate":
        # Determine input format and read accordingly
        if args.format == "binstr":
            binary = read_binary_string_file(args.input_file)
        elif args.format == "hexstr":
            # TODO: Implement hex string reading when needed
            logger.error("Hex string format not yet implemented for simulation input")
            sys.exit(1)
        else:  # "bin"
            binary = read_binary_file(args.input_file, args.allow_non_bin_ext)
        simulate_binary(
            binary,
            args.max_cycles,
            args.dump_memory,
            args.dump_registers,
            args.dump_memory_full,
        )

    elif args.command == "run":
        # Assemble and then simulate
        binary = assemble_file(args.input_file, args.output)
        simulate_binary(
            binary,
            args.max_cycles,
            args.dump_memory,
            args.dump_registers,
            args.dump_memory_full,
        )

    elif args.command == "mem-compare":
        # Compare two memory dump files
        success = compare_memory_dumps(
            args.file1, args.file2, args.ignore_comments, args.verbose
        )
        if not success:
            sys.exit(1)
