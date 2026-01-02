"""assembler.py - Assembler for the TTL CPU ISA
Author: Tom Riley
Date: 2025-07-20
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from turtle_toolkit.common.config import INSTRUCTION_WIDTH
from turtle_toolkit.common.data_types import DataBusValue, InstructionAddressBusValue
from turtle_toolkit.common.instruction_data import (
    ADDR_IMM_OPERAND,
    ARITH_LOGIC_IMM_OPCODE_TEXTS,
    ARITH_LOGIC_OPCODE_TEXTS,
    BRANCH_OPCODE_CONDITION_MAP,
    DATA_IMM_OPERAND,
    HALT_OPCODE_TEXTS,
    JUMP_IMM_OPCODE_TEXTS,
    JUMP_OPCODE_FUNC_MAP,
    JUMP_REG_OPCODE_TEXTS,
    NO_OPERAND,
    NOP_OPCODE_TEXTS,
    REG_OPERAND,
    ArithLogicFunction,
    BranchCondition,
    JumpFunction,
    Opcode,
    RegisterIndex,
    RegMemoryFunction,
)

# Regex: optional label + optional instruction + optional operand
LABEL_AND_INSTR_RE = re.compile(r"^\s*(?:(\w+):)?\s*(\w+)?(?:\s+(.+))?$")


@dataclass
class SourceLine:
    """Class to hold source line information for generating commented output."""

    line_number: int
    original_text: str
    instruction: Optional["Instruction"] = None
    is_instruction_line: bool = False


@dataclass
class Instruction:
    """Class to hold the instruction format and its components."""

    conditional_branch: bool = False  # Bit 0
    branch_conditon: Optional[BranchCondition] = None  # Bits 1-3
    opcode: Opcode = Opcode.ARITH_LOGIC_IMM  # Bits 1-3
    address_immediate: Optional[InstructionAddressBusValue] = None  # Bits 4-15
    function: ArithLogicFunction | RegMemoryFunction | JumpFunction = (
        ArithLogicFunction.ADD
    )  # Bits 4-7
    data_immediate: Optional[DataBusValue] = DataBusValue(0)  # Bits 8-15
    register: Optional[RegisterIndex] = None  # Bits 8-11
    source_line: Optional[str] = None  # Track original assembly line for comments


SymbolTable = Dict[str, int]


class Assembler:
    @staticmethod
    def parse_assembly(source: str) -> Tuple[List[Instruction], SymbolTable]:
        labels: SymbolTable = {}
        instructions: List[Instruction] = []
        unresolved_instructions: List[Tuple[Instruction, str, int]] = []  # (instruction, operand, address)
        address: int = 0

        lines = source.splitlines()

        # First pass: collect labels and parse instructions
        for line in lines:
            original_line = line  # Keep original line for comments
            line = line.split(";")[0].strip()  # Remove comments and whitespace
            if not line:
                continue

            match = LABEL_AND_INSTR_RE.match(line)
            if not match:
                raise SyntaxError(f"Invalid syntax: {line}")

            label: Optional[str]
            instr: Optional[str]
            operand: Optional[str]
            label, instr, operand = match.groups()

            if label:
                labels[label.upper()] = address  # Store labels in uppercase

            if instr:
                instr, operand = Assembler.replace_macros(instr, operand)
                try:
                    instruction = Assembler.parse_instruction(instr, operand)
                    instruction.source_line = original_line.strip()  # Store original line
                    instructions.append(instruction)
                except SyntaxError as e:
                    # Check if this is a label reference that needs to be resolved
                    if "Invalid immediate:" in str(e) and operand and instr.upper() in (BRANCH_OPCODE_CONDITION_MAP.keys() | JUMP_IMM_OPCODE_TEXTS):
                        # This is likely a label reference, defer resolution
                        instruction = Instruction()
                        if instr.upper() in BRANCH_OPCODE_CONDITION_MAP:
                            instruction.conditional_branch = True
                            instruction.branch_conditon = BRANCH_OPCODE_CONDITION_MAP[instr.upper()]
                        elif instr.upper() in JUMP_IMM_OPCODE_TEXTS:
                            instruction.opcode = Opcode.JUMP_IMM
                        instruction.source_line = original_line.strip()
                        instructions.append(instruction)
                        unresolved_instructions.append((instruction, operand.upper(), address))
                    else:
                        raise e
                address += INSTRUCTION_WIDTH // 8

        # Second pass: resolve label references
        for instruction, label_ref, instr_address in unresolved_instructions:
            if label_ref not in labels:
                raise SyntaxError(f"Undefined label: {label_ref}")
            
            target_address = labels[label_ref]
            # Calculate relative offset for branches (PC-relative addressing from current PC)
            offset = target_address - instr_address
            
            instruction.address_immediate = InstructionAddressBusValue(offset)

        return instructions, labels

    @staticmethod
    def replace_macros(instr: str, operand: Optional[str]) -> Tuple[str, Optional[str]]:
        """Replace macros with their corresponding instructions."""
        if instr in NOP_OPCODE_TEXTS:
            if operand is not None:
                raise SyntaxError(f"{instr} does not take an operand")
            return ArithLogicFunction.ADD.name + "I", "0"
        elif instr in HALT_OPCODE_TEXTS:
            if operand is not None:
                raise SyntaxError(f"{instr} does not take an operand")
            assert (
                len(JUMP_IMM_OPCODE_TEXTS) == 1
            ), "JUMP_IMM_OPCODE_TEXTS should have exactly one entry"
            return next(iter(JUMP_IMM_OPCODE_TEXTS)), "0"
        return instr, operand

    @staticmethod
    def parse_instruction(opcode: str, operand: Optional[str]) -> Instruction:
        opcode = opcode.upper().strip()
        operand = operand.upper().strip() if operand else None
        instruction = Instruction()
        instruction.conditional_branch = False

        if opcode in ARITH_LOGIC_OPCODE_TEXTS:
            instruction.opcode = Opcode.ARITH_LOGIC
            instruction.function = ArithLogicFunction[opcode]
        elif opcode in ARITH_LOGIC_IMM_OPCODE_TEXTS:
            instruction.opcode = Opcode.ARITH_LOGIC_IMM
            instruction.function = ArithLogicFunction[opcode[:-1]]
        elif opcode in RegMemoryFunction.__members__:
            instruction.opcode = Opcode.REG_MEMORY
            instruction.function = RegMemoryFunction[opcode]
        elif opcode in JUMP_REG_OPCODE_TEXTS:
            instruction.opcode = Opcode.JUMP_REG
            instruction.function = JUMP_OPCODE_FUNC_MAP[opcode]
        elif opcode in JUMP_IMM_OPCODE_TEXTS:
            instruction.opcode = Opcode.JUMP_IMM
        elif opcode in BRANCH_OPCODE_CONDITION_MAP:
            instruction.conditional_branch = True
            instruction.branch_conditon = BRANCH_OPCODE_CONDITION_MAP[opcode]

        if opcode in NO_OPERAND:
            if operand:
                raise SyntaxError(f"{opcode} does not take an operand")
            return instruction

        if not operand:
            raise SyntaxError(f"{opcode} requires an operand")

        if opcode in REG_OPERAND:
            if operand not in RegisterIndex.__members__:
                raise SyntaxError(f"Invalid register: {operand}")
            instruction.register = RegisterIndex[operand]
            return instruction

        if opcode in DATA_IMM_OPERAND:
            instruction.data_immediate = DataBusValue(
                Assembler.parse_immediate(operand)
            )
            return instruction

        if opcode in ADDR_IMM_OPERAND:
            instruction.address_immediate = InstructionAddressBusValue(
                Assembler.parse_immediate(operand)
            )
            return instruction

        raise SyntaxError(f"Unknown opcode: {opcode}")

    @staticmethod
    def parse_immediate(operand: str) -> int:
        operand = operand.strip().replace("_", "")
        if operand.startswith("0X"):
            return int(operand, 16)
        elif operand.startswith("0B"):
            return int(operand, 2)
        elif operand.lstrip("-").isdigit():
            return int(operand)
        raise SyntaxError(f"Invalid immediate: {operand}")

    @staticmethod
    def encode_instruction(instr: Instruction) -> bytes:
        binary = 0

        if instr.conditional_branch:
            binary |= 1  # Bit 0
            if instr.branch_conditon is None:
                raise ValueError("Branch condition is required for conditional branch")
            binary |= instr.branch_conditon.value << 1  # Bits 1–3
            if instr.address_immediate is None:
                raise ValueError("Address immediate is required for conditional branch")
            binary |= int(instr.address_immediate.unsigned_value()) << 4  # Bits 4–15
        else:
            binary |= instr.opcode.value << 1  # Bits 1–3

        if instr.opcode == Opcode.ARITH_LOGIC:
            binary |= instr.function.value << 4  # Bits 4–7
            if instr.function != ArithLogicFunction.INV:
                if instr.register is None:
                    raise ValueError("Register is required for ARITH_LOGIC")
                binary |= instr.register.value << 8  # Bits 8–11

        elif instr.opcode == Opcode.ARITH_LOGIC_IMM:
            binary |= instr.function.value << 4
            if instr.data_immediate is None:
                raise ValueError("Data immediate is required for ARITH_LOGIC_IMM")
            binary |= int(instr.data_immediate.unsigned_value()) << 8

        elif instr.opcode == Opcode.REG_MEMORY:
            binary |= instr.function.value << 4
            if instr.register is not None:
                binary |= instr.register.value << 8
            elif instr.data_immediate is not None:
                binary |= int(instr.data_immediate.unsigned_value()) << 8

        elif instr.opcode == Opcode.JUMP_IMM:
            if instr.address_immediate is None:
                raise ValueError("Address immediate is required for JUMP_IMM")
            binary |= int(instr.address_immediate.unsigned_value()) << 4

        elif instr.opcode == Opcode.JUMP_REG:
            binary |= instr.function.value << 4
            if instr.register is None:
                raise ValueError("Register is required for JUMP_REG")
            binary |= instr.register.value << 8

        return binary.to_bytes(2, byteorder="little")

    @staticmethod
    def assemble(source: str) -> bytes:
        """Assemble the source code into binary."""
        instructions, labels = Assembler.parse_assembly(source)
        binary = bytearray()
        for instr in instructions:
            binary.extend(Assembler.encode_instruction(instr))
        return bytes(binary)

    @staticmethod
    def assemble_with_source_info(source: str) -> Tuple[bytes, List[Instruction]]:
        """Assemble the source code into binary and return instructions with source line info."""
        instructions, labels = Assembler.parse_assembly(source)
        binary = bytearray()
        for instr in instructions:
            binary.extend(Assembler.encode_instruction(instr))
        return bytes(binary), instructions

    @staticmethod
    def assemble_with_full_source_info(source: str) -> Tuple[bytes, List[SourceLine]]:
        """Assemble source code and return binary with complete source line information."""
        source_lines = []
        instructions: List[Instruction] = []
        unresolved_instructions: List[Tuple[Instruction, str, int]] = []  # (instruction, operand, address)
        labels: SymbolTable = {}
        address = 0

        lines = source.splitlines()

        # First pass: collect labels and parse instructions
        for line_number, line in enumerate(lines, 1):
            original_line = line
            source_line = SourceLine(
                line_number=line_number,
                original_text=original_line,
                instruction=None,
                is_instruction_line=False,
            )

            # Parse the line for instructions
            clean_line = line.split(";")[0].strip()  # Remove comments and whitespace
            if clean_line:
                match = LABEL_AND_INSTR_RE.match(clean_line)
                if match:
                    label: Optional[str]
                    instr: Optional[str]
                    operand: Optional[str]
                    label, instr, operand = match.groups()

                    if label:
                        labels[label.upper()] = address  # Store labels in uppercase

                    if instr:
                        instr, operand = Assembler.replace_macros(instr, operand)
                        try:
                            instruction = Assembler.parse_instruction(instr, operand)
                            instruction.source_line = original_line.strip()
                            source_line.instruction = instruction
                            source_line.is_instruction_line = True
                            instructions.append(instruction)
                        except SyntaxError as e:
                            # Check if this is a label reference that needs to be resolved
                            if "Invalid immediate:" in str(e) and operand and instr.upper() in (BRANCH_OPCODE_CONDITION_MAP.keys() | JUMP_IMM_OPCODE_TEXTS):
                                # This is likely a label reference, defer resolution
                                instruction = Instruction()
                                if instr.upper() in BRANCH_OPCODE_CONDITION_MAP:
                                    instruction.conditional_branch = True
                                    instruction.branch_conditon = BRANCH_OPCODE_CONDITION_MAP[instr.upper()]
                                elif instr.upper() in JUMP_IMM_OPCODE_TEXTS:
                                    instruction.opcode = Opcode.JUMP_IMM
                                instruction.source_line = original_line.strip()
                                source_line.instruction = instruction
                                source_line.is_instruction_line = True
                                instructions.append(instruction)
                                unresolved_instructions.append((instruction, operand.upper(), address))
                            else:
                                raise e
                        address += INSTRUCTION_WIDTH // 8

            source_lines.append(source_line)

        # Second pass: resolve label references
        for instruction, label_ref, instr_address in unresolved_instructions:
            if label_ref not in labels:
                raise SyntaxError(f"Undefined label: {label_ref}")
            
            target_address = labels[label_ref]
            # Calculate relative offset for branches (PC-relative addressing from current PC)
            offset = target_address - instr_address
            
            instruction.address_immediate = InstructionAddressBusValue(offset)

        # Generate binary
        binary = bytearray()
        for instruction in instructions:
            binary.extend(Assembler.encode_instruction(instruction))

        return bytes(binary), source_lines

    @staticmethod
    def assemble_to_binary_string(
        source_code: str,
        input_filename: str,
        comment_level: str = "stripped",
        one_byte_per_line: bool = False,
    ) -> Tuple[bytes, str]:
        """
        Assemble source code and return binary with binary string format.

        Args:
            source_code: The assembly source code
            input_filename: Name of the input file (for comments)
            comment_level: 'none', 'stripped', or 'full'

        Returns:
            Tuple of (binary_data, binary_string)
        """
        if comment_level == "full":
            binary, source_lines = Assembler.assemble_with_full_source_info(source_code)
            formatted_text = Assembler.format_binary_string(
                binary=binary,
                input_filename=input_filename,
                comment_level=comment_level,
                source_lines=source_lines,
                one_byte_per_line=one_byte_per_line,
            )
        elif comment_level == "stripped":
            binary, instructions = Assembler.assemble_with_source_info(source_code)
            formatted_text = Assembler.format_binary_string(
                binary=binary,
                input_filename=input_filename,
                comment_level=comment_level,
                instructions=instructions,
                one_byte_per_line=one_byte_per_line,
            )
        else:  # comment_level == "none"
            binary = Assembler.assemble(source_code)
            formatted_text = Assembler.format_binary_string(
                binary=binary,
                input_filename=input_filename,
                comment_level=comment_level,
                one_byte_per_line=one_byte_per_line,
            )

        return binary, formatted_text

    @staticmethod
    def assemble_to_hex_string(
        source_code: str,
        input_filename: str,
        comment_level: str = "stripped",
    ) -> Tuple[bytes, str]:
        """
        Assemble source code and return binary with hex string format.

        Args:
            source_code: The assembly source code
            input_filename: Name of the input file (for comments)
            comment_level: 'none', 'stripped', or 'full'

        Returns:
            Tuple of (binary_data, hex_string)
        """
        if comment_level == "full":
            binary, source_lines = Assembler.assemble_with_full_source_info(source_code)
            formatted_text = OutputFormatter.format_hex_string_full(
                binary, input_filename, source_lines
            )
        elif comment_level == "stripped":
            binary, instructions = Assembler.assemble_with_source_info(source_code)
            formatted_text = OutputFormatter.format_hex_string_stripped(
                binary, input_filename, instructions
            )
        else:  # comment_level == "none"
            binary = Assembler.assemble(source_code)
            formatted_text = OutputFormatter.format_hex_string_none(binary)

        return binary, formatted_text

    @staticmethod
    def format_binary_string(
        *,
        binary: bytes,
        input_filename: str,
        comment_level: str = "stripped",
        instructions: Optional[List[Instruction]] = None,
        source_lines: Optional[List[SourceLine]] = None,
        one_byte_per_line: bool = False,
    ) -> str:
        """Format already-assembled binary as a .binstr text file.

        This is intentionally separated from assembly so callers can pad `binary`
        to a fixed length before formatting.
        """
        if one_byte_per_line:
            if comment_level == "full":
                raise ValueError(
                    "one_byte_per_line output is not compatible with comment_level='full' "
                    "(full output includes non-instruction lines and is not a memory image)."
                )
            if comment_level == "stripped" and instructions is not None:
                return OutputFormatter.format_binary_string_stripped_bytes(
                    binary, input_filename, instructions
                )
            return OutputFormatter.format_binary_string_none_bytes(binary)

        if comment_level == "full":
            if source_lines is None:
                raise ValueError("source_lines must be provided for comment_level='full'")
            return OutputFormatter.format_binary_string_full(
                binary, input_filename, source_lines
            )
        if comment_level == "stripped":
            if instructions is None:
                raise ValueError(
                    "instructions must be provided for comment_level='stripped'"
                )
            return OutputFormatter.format_binary_string_stripped(
                binary, input_filename, instructions
            )
        return OutputFormatter.format_binary_string_none(binary)

    @staticmethod
    def format_hex_string(
        *,
        binary: bytes,
        input_filename: str,
        comment_level: str = "stripped",
        instructions: Optional[List[Instruction]] = None,
        source_lines: Optional[List[SourceLine]] = None,
    ) -> str:
        """Format already-assembled binary as a .hexstr text file."""
        if comment_level == "full":
            if source_lines is None:
                raise ValueError("source_lines must be provided for comment_level='full'")
            return OutputFormatter.format_hex_string_full(binary, input_filename, source_lines)
        if comment_level == "stripped":
            if instructions is None:
                raise ValueError(
                    "instructions must be provided for comment_level='stripped'"
                )
            return OutputFormatter.format_hex_string_stripped(binary, input_filename, instructions)
        return OutputFormatter.format_hex_string_none(binary)


class OutputFormatter:
    """Handles formatting of assembled binary data into various text formats."""

    @staticmethod
    def format_binary_string_none(binary: bytes) -> str:
        """Format binary data as plain binary string with no comments."""
        return (
            "\n".join(
                f"{binary[i]:08b} {binary[i+1]:08b}" for i in range(0, len(binary), 2)
            )
            + "\n"
        )

    @staticmethod
    def format_binary_string_none_bytes(binary: bytes) -> str:
        """Format binary data as one byte per line (memory image for $readmemb)."""
        return "\n".join(f"{b:08b}" for b in binary) + "\n"

    @staticmethod
    def format_binary_string_stripped(
        binary: bytes,
        input_filename: str,
        instructions: List[Instruction],
    ) -> str:
        """Format binary data as binary string with stripped assembly comments."""
        binary_str = f"// Assembled from: {os.path.basename(input_filename)}\n"

        byte_index = 0
        for instruction in instructions:
            if byte_index < len(binary):
                # Each instruction is 2 bytes (16 bits)
                byte1 = binary[byte_index] if byte_index < len(binary) else 0
                byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0

                # Format as binary strings
                binary_line = f"{byte1:08b} {byte2:08b}"

                # Add comment with original assembly line (stripped of comments)
                if instruction.source_line:
                    source_comment = instruction.source_line.split(";")[0].strip()
                    binary_str += f"{binary_line:<18} // {source_comment}\n"
                else:
                    binary_str += f"{binary_line}\n"

                byte_index += 2

        # Handle any remaining padding bytes
        while byte_index < len(binary):
            byte1 = binary[byte_index] if byte_index < len(binary) else 0
            byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
            binary_line = f"{byte1:08b} {byte2:08b}"
            binary_str += f"{binary_line}\n"
            byte_index += 2

        return binary_str

    @staticmethod
    def format_binary_string_stripped_bytes(
        binary: bytes,
        input_filename: str,
        instructions: List[Instruction],
    ) -> str:
        """Format binary data as one byte per line, with stripped instruction comments.

        Each instruction emits two lines (opcode byte then operand byte). Any extra
        padding bytes beyond the instruction stream are emitted with no comments.
        """
        binary_str = f"// Assembled from: {os.path.basename(input_filename)}\n"

        byte_index = 0
        for instruction in instructions:
            if byte_index >= len(binary):
                break

            byte1 = binary[byte_index]
            byte2 = binary[byte_index + 1] if (byte_index + 1) < len(binary) else 0
            line1 = f"{byte1:08b}"
            line2 = f"{byte2:08b}"

            if instruction.source_line:
                source_comment = instruction.source_line.split(";")[0].strip()
                binary_str += f"{line1:<8} // {source_comment}\n"
            else:
                binary_str += f"{line1}\n"

            binary_str += f"{line2}\n"
            byte_index += 2

        while byte_index < len(binary):
            binary_str += f"{binary[byte_index]:08b}\n"
            byte_index += 1

        return binary_str

    @staticmethod
    def format_binary_string_full(
        binary: bytes,
        input_filename: str,
        source_lines: List[SourceLine],
    ) -> str:
        """Format binary data as binary string with full source comments and spacing."""
        binary_str = f"// Assembled from: {os.path.basename(input_filename)}\n"

        instruction_index = 0

        for source_line in source_lines:
            if source_line.is_instruction_line and source_line.instruction:
                # Calculate byte position for this instruction
                byte_index = instruction_index * 2
                if byte_index < len(binary):
                    byte1 = binary[byte_index] if byte_index < len(binary) else 0
                    byte2 = (
                        binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
                    )
                    binary_line = f"{byte1:08b} {byte2:08b}"
                    binary_str += f"{binary_line:<18} // {source_line.original_text}\n"
                    instruction_index += 1
            else:
                # Non-instruction line (comment, blank line, etc.)
                binary_str += f"{'':18} // {source_line.original_text}\n"

        # Handle any remaining padding bytes
        byte_index = instruction_index * 2
        while byte_index < len(binary):
            byte1 = binary[byte_index] if byte_index < len(binary) else 0
            byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
            binary_line = f"{byte1:08b} {byte2:08b}"
            binary_str += f"{binary_line}\n"
            byte_index += 2

        return binary_str

    @staticmethod
    def format_hex_string_none(binary: bytes) -> str:
        """Format binary data as plain hex string with no comments."""
        return (
            "\n".join(
                f"{binary[i]:02x} {binary[i+1]:02x}" for i in range(0, len(binary), 2)
            )
            + "\n"
        )

    @staticmethod
    def format_hex_string_stripped(
        binary: bytes,
        input_filename: str,
        instructions: List[Instruction],
    ) -> str:
        """Format binary data as hex string with stripped assembly comments."""
        hex_str = f"// Assembled from: {os.path.basename(input_filename)}\n"

        byte_index = 0
        for instruction in instructions:
            if byte_index < len(binary):
                # Each instruction is 2 bytes (16 bits)
                byte1 = binary[byte_index] if byte_index < len(binary) else 0
                byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0

                # Format as hex strings
                hex_line = f"{byte1:02x} {byte2:02x}"

                # Add comment with original assembly line (stripped of comments)
                if instruction.source_line:
                    source_comment = instruction.source_line.split(";")[0].strip()
                    hex_str += f"{hex_line:<6} // {source_comment}\n"
                else:
                    hex_str += f"{hex_line}\n"

                byte_index += 2

        # Handle any remaining padding bytes
        while byte_index < len(binary):
            byte1 = binary[byte_index] if byte_index < len(binary) else 0
            byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
            hex_line = f"{byte1:02x} {byte2:02x}"
            hex_str += f"{hex_line}\n"
            byte_index += 2

        return hex_str

    @staticmethod
    def format_hex_string_full(
        binary: bytes,
        input_filename: str,
        source_lines: List[SourceLine],
    ) -> str:
        """Format binary data as hex string with full source comments and spacing."""
        hex_str = f"// Assembled from: {os.path.basename(input_filename)}\n"

        instruction_index = 0

        for source_line in source_lines:
            if source_line.is_instruction_line and source_line.instruction:
                # Calculate byte position for this instruction
                byte_index = instruction_index * 2
                if byte_index < len(binary):
                    byte1 = binary[byte_index] if byte_index < len(binary) else 0
                    byte2 = (
                        binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
                    )
                    hex_line = f"{byte1:02x} {byte2:02x}"
                    hex_str += f"{hex_line:<6} // {source_line.original_text}\n"
                    instruction_index += 1
            else:
                # Non-instruction line (comment, blank line, etc.)
                hex_str += f"{'':6} // {source_line.original_text}\n"

        # Handle any remaining padding bytes
        byte_index = instruction_index * 2
        while byte_index < len(binary):
            byte1 = binary[byte_index] if byte_index < len(binary) else 0
            byte2 = binary[byte_index + 1] if byte_index + 1 < len(binary) else 0
            hex_line = f"{byte1:02x} {byte2:02x}"
            hex_str += f"{hex_line}\n"
            byte_index += 2

        return hex_str
