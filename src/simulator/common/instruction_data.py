"""instruction_data.py - Common data about instruction formats
Author: Tom Riley
Date: 2025-05-10
"""

from enum import Enum


class Opcode(Enum):
    ARITH_LOGIC_IMM = 0b000
    ARITH_LOGIC = 0b001
    REG_MEMORY = 0b010
    JUMP_IMM = 0b100
    JUMP_REG = 0b111


class ArithLogicFunction(Enum):
    """Enum for ALU operations."""

    ADD = 0b0000
    SUB = 0b0001
    AND = 0b0010
    OR = 0b0100
    XOR = 0b0101
    INV = 0b0111


class RegMemoryFunction(Enum):
    LOAD = 0b0000
    STORE = 0b0001
    GET = 0b0010
    PUT = 0b0011
    SET = 0b0100


class JumpFunction(Enum):
    JUMP_RELATIVE = 0b0000
    JUMP_ABSOLUTE = 0b0001


class BranchCondition(Enum):
    ZERO = 0b000
    NOT_ZERO = 0b001
    POSITIVE = 0b010
    NEGATIVE = 0b011
    CARRY_SET = 0b100
    CARRY_CLEARED = 0b101
    OVERFLOW_SET = 0b110
    OVERFLOW_CLEARED = 0b111


class RegisterIndex(Enum):
    """Enum for register indices."""

    R0 = 0b0000
    R1 = 0b0001
    R2 = 0b0010
    R3 = 0b0011
    R4 = 0b0100
    R5 = 0b0101
    R6 = 0b0110
    R7 = 0b0111
    ACC = 0b1000
    DBAR = 0b1001
    DOFF = 0b1010
    IBAR = 0b1101
    IOFF = 0b1110
    STATUS = 0b1111


NOP_OPCODE_TEXTS = {"NOP"}

HALT_OPCODE_TEXTS = {"HALT"}

ARITH_LOGIC_OPCODE_TEXTS = set(ArithLogicFunction.__members__.keys())

ARITH_LOGIC_IMM_OPCODE_TEXTS = set(
    f"{f.name}I" for f in ArithLogicFunction if f != ArithLogicFunction.INV
)

REG_OPCODE_TEXTS = {"GET", "PUT"}

REG_IMM_OPCODE_TEXTS = {
    "SET",
}

MEMORY_OPCODE_TEXTS = {"LOAD", "STORE"}

JUMP_IMM_OPCODE_TEXTS = {
    "JMPI",
}


JUMP_OPCODE_FUNC_MAP = {
    "JMPR": JumpFunction.JUMP_RELATIVE,
    "JMP": JumpFunction.JUMP_ABSOLUTE,
}

JUMP_REG_OPCODE_TEXTS = set(JUMP_OPCODE_FUNC_MAP.keys())

BRANCH_OPCODE_CONDITION_MAP = {
    "BZ": BranchCondition.ZERO,
    "BNZ": BranchCondition.NOT_ZERO,
    "BP": BranchCondition.POSITIVE,
    "BN": BranchCondition.NEGATIVE,
    "BCS": BranchCondition.CARRY_SET,
    "BCC": BranchCondition.CARRY_CLEARED,
    "BOS": BranchCondition.OVERFLOW_SET,
    "BOC": BranchCondition.OVERFLOW_CLEARED,
}

BRANCH_OPCODE_TEXTS = set(BRANCH_OPCODE_CONDITION_MAP.keys())

NO_OPERAND = JUMP_REG_OPCODE_TEXTS | MEMORY_OPCODE_TEXTS | {ArithLogicFunction.INV.name}
REG_OPERAND = REG_OPCODE_TEXTS | ARITH_LOGIC_OPCODE_TEXTS - {
    ArithLogicFunction.INV.name
}
DATA_IMM_OPERAND = ARITH_LOGIC_IMM_OPCODE_TEXTS | REG_IMM_OPCODE_TEXTS
ADDR_IMM_OPERAND = JUMP_IMM_OPCODE_TEXTS | BRANCH_OPCODE_TEXTS


assert (enum_keys := set(RegMemoryFunction.__members__.keys())) == (
    tuple_lists := (REG_OPCODE_TEXTS | MEMORY_OPCODE_TEXTS | REG_IMM_OPCODE_TEXTS)
), f"Enum keys {enum_keys} do not match expected list {tuple_lists}"
