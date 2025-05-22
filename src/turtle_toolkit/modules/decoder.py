"""decoder.py - Decode Unit module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from turtle_toolkit.common.data_types import DataBusValue, InstructionAddressBusValue
from turtle_toolkit.common.instruction_data import (
    ArithLogicFunction,
    BranchCondition,
    JumpFunction,
    Opcode,
    RegisterIndex,
    RegMemoryFunction,
)
from turtle_toolkit.modules.base_module import BaseModule
from turtle_toolkit.modules.instruction_memory import InstructionBinary


@dataclass
class DecodedInstruction:
    """Class to hold the decoded instruction."""

    # Halt
    halt_instruction: bool

    # Branch
    branch_instruction: bool
    branch_condition: BranchCondition
    immediate_address_value: InstructionAddressBusValue

    # ALU
    alu_instruction: bool
    alu_immediate_instruction: bool
    alu_function: Optional[ArithLogicFunction]
    register_index: RegisterIndex
    immediate_data_value: DataBusValue

    # Register File
    register_file_instruction: bool
    register_file_set: bool
    register_file_get: bool
    register_file_put: bool

    # Memory
    memory_instruction: bool
    memory_load: bool
    memory_store: bool

    # Jump
    jump_instruction: bool
    immediate_jump: bool
    relative_jump: bool


class DecodeUnit(BaseModule):
    def decode(self, instruction_binary: InstructionBinary) -> DecodedInstruction:
        inst = int.from_bytes(instruction_binary.data, byteorder="little")

        branch_field = (inst >> 0) & 0x01
        branch_cond_field = (inst >> 1) & 0b111
        op_field = (inst >> 1) & 0b111
        addr_imm_field = (inst >> 4) & 0xFFF
        func_field = (inst >> 4) & 0xF
        reg_idx_field = (inst >> 8) & 0xF
        data_imm_field = (inst >> 8) & 0xFF

        return DecodedInstruction(
            halt_instruction=(
                branch_field == 0
                and op_field == Opcode.JUMP_IMM.value
                and addr_imm_field == 0
            ),
            branch_instruction=(branch_field == 1),
            branch_condition=BranchCondition(branch_cond_field),
            immediate_address_value=InstructionAddressBusValue(
                np.uint16(addr_imm_field)
            ),
            alu_instruction=(
                is_alu := (
                    branch_field == 0
                    and (
                        op_field == Opcode.ARITH_LOGIC_IMM.value
                        or op_field == Opcode.ARITH_LOGIC.value
                    )
                )
            ),
            alu_immediate_instruction=(op_field == Opcode.ARITH_LOGIC_IMM.value),
            alu_function=ArithLogicFunction(func_field) if is_alu else None,
            register_index=RegisterIndex(reg_idx_field),
            immediate_data_value=DataBusValue(np.uint16(data_imm_field)),
            register_file_instruction=(
                branch_field == 0
                and op_field == Opcode.REG_MEMORY.value
                and func_field != RegMemoryFunction.LOAD.value
                and func_field != RegMemoryFunction.STORE.value
            ),
            register_file_set=(func_field == RegMemoryFunction.SET.value),
            register_file_get=(func_field == RegMemoryFunction.GET.value),
            register_file_put=(func_field == RegMemoryFunction.PUT.value),
            memory_instruction=(
                branch_field == 0
                and op_field == Opcode.REG_MEMORY.value
                and (
                    func_field == RegMemoryFunction.LOAD.value
                    or func_field == RegMemoryFunction.STORE.value
                )
            ),
            memory_load=(func_field == RegMemoryFunction.LOAD.value),
            memory_store=(func_field == RegMemoryFunction.STORE.value),
            jump_instruction=(
                branch_field == 0
                and (
                    op_field == Opcode.JUMP_IMM.value
                    or op_field == Opcode.JUMP_REG.value
                )
            ),
            immediate_jump=(op_field == Opcode.JUMP_IMM.value),
            relative_jump=(func_field == JumpFunction.JUMP_RELATIVE.value),
        )
