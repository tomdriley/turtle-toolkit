"""decoder.py - Decode Unit module
Author: Tom Riley
Date: 2025-05-04
"""

from enum import Enum
from simulator.modules.base_module import BaseModule
from simulator.modules.instruction_memory import Instruction
from simulator.common.data_types import DataBusValue, InstructionAddressBusValue
from simulator.modules.register_file import RegisterIndex
from simulator.modules.alu import ArithLogicFunction


class BranchCondition(Enum):
    ZERO = 0b000
    NOT_ZERO = 0b001
    POSITIVE = 0b010
    NEGATIVE = 0b011
    CARRY_SET = 0b100
    CARRY_CLEARED = 0b101
    OVERFLOW_SET = 0b110
    OVERFLOW_CLEARED = 0b111


class DecodedInstruction:
    """Class to hold the decoded instruction."""

    alu_instruction: bool
    memory_instruction: bool
    register_file_instruction: bool
    branch_instruction: bool
    jump_instruction: bool
    immediate_address_value: InstructionAddressBusValue
    memory_load: bool
    memory_store: bool
    alu_immediate_instruction: bool
    register_file_set: bool
    register_file_get: bool
    register_file_put: bool
    immediate_data_value: DataBusValue
    register_index: RegisterIndex
    alu_function: ArithLogicFunction
    immediate_jump: bool
    relative_jump: bool
    register_jump: bool
    branch_condition: BranchCondition
    halt_instruction: bool
    nop_instruction: bool


class DecodeUnit(BaseModule):
    def decode(self, instruction: Instruction) -> DecodedInstruction:
        raise NotImplementedError()
