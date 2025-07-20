"""cli.py - Set up command line arg parser for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

import argparse
from enum import Enum
from importlib.metadata import metadata

from turtle_toolkit.common.logger import configure_logger

PROJECT_METADATA = metadata("turtle_toolkit")
PROJECT_NAME = PROJECT_METADATA["Name"]
PROJECT_VERSION = PROJECT_METADATA["Version"]
PROJECT_DESCRIPTION = PROJECT_METADATA["Summary"]


class AssemblerFormats(Enum):
    """Enumeration for assembler output formats."""

    BIN = "bin"
    BINARY_STRING = "binstr"
    HEX_STRING = "hexstr"


class CommentLevel(Enum):
    """Enumeration for comment levels in text output formats."""

    NONE = "none"  # No comments, just binary/hex
    STRIPPED = "stripped"  # Only instruction lines with comments stripped
    FULL = "full"  # Full source with all comments and blank lines


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
    assemble_parser.add_argument(
        "-f",
        "--format",
        type=lambda x: AssemblerFormats(x),
        choices=list(AssemblerFormats),
        help="Output format. Choices are 'bin' (for binary), 'binstr' (for binary string), or 'hexstr' (for hex string). Default is 'bin'.",
        default=AssemblerFormats.BIN,
    )
    assemble_parser.add_argument(
        "-c",
        "--comments",
        type=lambda x: CommentLevel(x),
        choices=list(CommentLevel),
        help="Comment level for text formats. 'none' = no comments, 'stripped' = instruction lines only, 'full' = all source lines. Default is 'stripped'.",
        default=CommentLevel.STRIPPED,
    )
    assemble_parser.add_argument(
        "-l",
        "--output-length",
        type=int,
        default=0,
        help="Length of output binary file in bytes. If 0, the assembler will determine the length automatically.",
    )

    # Simulator command
    simulate_parser = subparsers.add_parser("simulate", help="Simulate binary code")
    simulate_parser.add_argument("input_file", type=str, help="File to simulate")
    simulate_parser.add_argument(
        "-f",
        "--format",
        choices=[f.value for f in AssemblerFormats],
        help="Input format. 'bin' (for binary), 'binstr' (for binary string), or 'hexstr' (for hex string). Default is 'bin'.",
        default="bin",
    )
    simulate_parser.add_argument(
        "-m",
        "--max-cycles",
        type=int,
        default=None,
        help="Maximum number of cycles to simulate as a watchdog timer (default: no limit - run until HALT)",
    )
    simulate_parser.add_argument(
        "--allow-non-bin-ext",
        action="store_true",
        help="Allow non-.bin file extensions for binary files (deprecated - use --format instead)",
    )
    simulate_parser.add_argument(
        "--dump-memory",
        type=str,
        help="Dump final data memory state to file (binary string format with comments)",
    )
    simulate_parser.add_argument(
        "--dump-memory-full",
        action="store_true",
        help="When dumping memory, include entire address space with zeros for unwritten locations",
    )
    simulate_parser.add_argument(
        "--dump-registers",
        type=str,
        help="Dump final register file state to file (binary string format with comments)",
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
        default=None,
        help="Maximum number of cycles to simulate as a watchdog timer (default: no limit - run until HALT)",
    )
    combined_parser.add_argument(
        "--dump-memory",
        type=str,
        help="Dump final data memory state to file (binary string format with comments)",
    )
    combined_parser.add_argument(
        "--dump-memory-full",
        action="store_true",
        help="When dumping memory, include entire address space with zeros for unwritten locations",
    )
    combined_parser.add_argument(
        "--dump-registers",
        type=str,
        help="Dump final register file state to file (binary string format with comments)",
    )

    # Compare command
    compare_parser = subparsers.add_parser(
        "mem-compare", help="Compare two memory dump files"
    )
    compare_parser.add_argument("file1", type=str, help="First dump file to compare")
    compare_parser.add_argument("file2", type=str, help="Second dump file to compare")
    compare_parser.add_argument(
        "--ignore-comments",
        action="store_true",
        default=True,
        help="Ignore comments when comparing (default: True)",
    )
    compare_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed comparison output",
    )

    return parser.parse_args()


def setup_cli() -> argparse.Namespace:
    args = parse_args()
    configure_logger(args.verbose)
    return args
