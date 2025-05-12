"""assembler.py - Assembler helper script

This script provides functionality to convert assembly language
instructions into binary format. It includes a simple assembler
that can parse a limited set of instructions and convert them
into their binary representations.

Author: Tom Riley
Date: 2025-05-07
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from simulator.common.config import INSTRUCTION_WIDTH
from simulator.common.data_types import DataBusValue, InstructionAddressBusValue
from simulator.common.instruction_data import RegisterIndex
from simulator.common.instruction_data import (
    ArithLogicFunction,
    BranchCondition,
    JumpFunction,
    Opcode,
    RegMemoryFunction,
    JUMP_OPCODE_FUNC_MAP,
    JUMP_REG_OPCODE_TEXTS,
    JUMP_IMM_OPCODE_TEXTS,
    ARITH_LOGIC_OPCODE_TEXTS,
    ARITH_LOGIC_IMM_OPCODE_TEXTS,
    NO_OPERAND,
    DATA_IMM_OPERAND,
    ADDR_IMM_OPERAND,
    REG_OPERAND,
    BRANCH_OPCODE_CONDITION_MAP,
    NOP_OPCODE_TEXTS,
    HALT_OPCODE_TEXTS,
)

# Regex: optional label + optional instruction + optional operand
LABEL_AND_INSTR_RE = re.compile(r"^\s*(?:(\w+):)?\s*(\w+)?(?:\s+(.+))?$")


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


SymbolTable = Dict[str, int]


class Assembler:
    @staticmethod
    def parse_assembly(source: str) -> Tuple[List[Instruction], SymbolTable]:
        labels: SymbolTable = {}
        instructions: List[Instruction] = []
        address: int = 0

        lines = source.splitlines()

        for line in lines:
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
                labels[label] = address

            if instr:
                instr, operand = Assembler.replace_macros(instr, operand)
                instructions.append(Assembler.parse_instruction(instr, operand))
                address += INSTRUCTION_WIDTH // 8

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
