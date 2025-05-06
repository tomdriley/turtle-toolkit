"""decoder.py - Decode Unit module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule
from simulator.modules.instruction_memory import Instruction
from simulator.common.data_types import DataBusValue, InstructionAddressBusValue
from simulator.modules.register_file import RegisterIndex
from simulator.modules.alu import ALUFunction


class BranchCondition:
    pass


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
    alu_function: ALUFunction
    immediate_jump: bool
    relative_jump: bool
    register_jump: bool
    branch_condition: BranchCondition
    halt_instruction: bool
    nop_instruction: bool


class DecodeUnit(BaseModule):
    def decode(self, instruction: Instruction) -> DecodedInstruction:
        raise NotImplementedError()
