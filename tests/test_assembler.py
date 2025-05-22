import numpy as np
import pytest

from turtle_toolkit.assembler import Assembler, Opcode, RegMemoryFunction
from turtle_toolkit.common.data_types import DataBusValue, InstructionAddressBusValue
from turtle_toolkit.common.instruction_data import RegisterIndex
from turtle_toolkit.modules.alu import ArithLogicFunction
from turtle_toolkit.modules.decoder import BranchCondition

from .binary_macros import INSTRUCTION_HALT, INSTRUCTION_NOP


def test_parse_assembly():
    source = """
    START: ADD R0
    SUBI 0x10
    JMP
    END: INV
    """
    instructions, labels = Assembler.parse_assembly(source)

    assert labels == {"START": 0, "END": 6}
    assert len(instructions) == 4

    assert instructions[0].opcode == Opcode.ARITH_LOGIC
    assert instructions[0].function == ArithLogicFunction.ADD
    assert instructions[0].register == RegisterIndex.R0

    assert instructions[1].opcode == Opcode.ARITH_LOGIC_IMM
    assert instructions[1].function == ArithLogicFunction.SUB
    assert instructions[1].data_immediate == 0x10

    assert instructions[2].opcode == Opcode.JUMP_REG

    assert instructions[3].opcode == Opcode.ARITH_LOGIC
    assert instructions[3].function == ArithLogicFunction.INV


def test_parse_branch_instructions():
    source = """
    BZ 0x04
    BNZ 0x08
    BP 0x0C
    BN 0x10
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 4

    assert instructions[0].conditional_branch
    assert instructions[0].branch_conditon == BranchCondition.ZERO
    assert instructions[0].address_immediate == InstructionAddressBusValue(
        np.int16(0x04)
    )

    assert instructions[1].conditional_branch
    assert instructions[1].branch_conditon == BranchCondition.NOT_ZERO
    assert instructions[1].address_immediate == InstructionAddressBusValue(
        np.int16(0x08)
    )

    assert instructions[2].conditional_branch
    assert instructions[2].branch_conditon == BranchCondition.POSITIVE
    assert instructions[2].address_immediate == InstructionAddressBusValue(0x0C)

    assert instructions[3].conditional_branch
    assert instructions[3].branch_conditon == BranchCondition.NEGATIVE
    assert instructions[3].address_immediate == InstructionAddressBusValue(
        np.int16(0x10)
    )


def test_invalid_syntax():
    with pytest.raises(SyntaxError):
        Assembler.parse_assembly("INVALID INSTRUCTION")


def test_memory_instructions():
    source = """
    LOAD
    STORE
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 2

    assert instructions[0].opcode == Opcode.REG_MEMORY
    assert instructions[0].function == RegMemoryFunction.LOAD

    assert instructions[1].opcode == Opcode.REG_MEMORY
    assert instructions[1].function == RegMemoryFunction.STORE


def test_immediate_values():
    source = """
    ADDI 0xFF
    SUBI 0b1010
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 2

    assert instructions[0].opcode == Opcode.ARITH_LOGIC_IMM
    assert instructions[0].function == ArithLogicFunction.ADD
    assert instructions[0].data_immediate == DataBusValue(0xFF)

    assert instructions[1].opcode == Opcode.ARITH_LOGIC_IMM
    assert instructions[1].function == ArithLogicFunction.SUB
    assert instructions[1].data_immediate == DataBusValue(np.int16(0b1010))


def test_nop():
    source = """
    ADDI 0
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 1
    assert instructions[0].opcode == Opcode.ARITH_LOGIC_IMM
    assert instructions[0].function == ArithLogicFunction.ADD
    assert instructions[0].data_immediate == DataBusValue(np.int16(0x00))

    binary = Assembler.encode_instruction(instructions[0])
    assert binary == INSTRUCTION_NOP


def test_halt():
    source = """
    JMPI 0
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 1
    assert instructions[0].opcode == Opcode.JUMP_IMM
    assert instructions[0].address_immediate == InstructionAddressBusValue(np.uint16(0))

    binary = Assembler.encode_instruction(instructions[0])
    assert binary == INSTRUCTION_HALT


def test_nop_macro():
    source = """
    NOP
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 1
    assert instructions[0].opcode == Opcode.ARITH_LOGIC_IMM
    assert instructions[0].function == ArithLogicFunction.ADD
    assert instructions[0].data_immediate == DataBusValue(np.int16(0x00))

    binary = Assembler.encode_instruction(instructions[0])
    assert binary == INSTRUCTION_NOP


def test_halt_macro():
    source = """
    HALT
    """
    instructions, _ = Assembler.parse_assembly(source)

    assert len(instructions) == 1
    assert instructions[0].opcode == Opcode.JUMP_IMM
    assert instructions[0].address_immediate == InstructionAddressBusValue(np.uint16(0))

    binary = Assembler.encode_instruction(instructions[0])
    assert binary == INSTRUCTION_HALT
