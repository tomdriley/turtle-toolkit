import numpy as np
import pytest

from turtle_toolkit.assembler import Assembler
from turtle_toolkit.common.instruction_data import ArithLogicFunction, BranchCondition
from turtle_toolkit.modules.decoder import DecodeUnit
from turtle_toolkit.modules.instruction_memory import InstructionBinary

from .binary_macros import INSTRUCTION_HALT, INSTRUCTION_NOP


@pytest.fixture
def decoder():
    return DecodeUnit("test_decoder")


def test_decode_nop_instruction(decoder):
    # Example binary for NOP instruction
    binary_data = InstructionBinary(INSTRUCTION_NOP)
    decoded = decoder.decode(binary_data)
    assert not decoded.halt_instruction


def test_decode_halt_instruction(decoder):
    # Example binary for HALT instruction
    binary_data = InstructionBinary(INSTRUCTION_HALT)
    decoded = decoder.decode(binary_data)
    assert decoded.halt_instruction


def test_decode_alu_instruction(decoder):
    # Example binary for ALU ADD instruction
    binary_data = InstructionBinary(Assembler.assemble("ADD R0"))
    decoded = decoder.decode(binary_data)
    assert decoded.alu_instruction
    assert decoded.alu_function == ArithLogicFunction.ADD


def test_decode_branch_instruction(decoder):
    # Example binary for branch instruction with ZERO condition
    binary_data = InstructionBinary(Assembler.assemble("BZ 0x04"))
    decoded = decoder.decode(binary_data)
    assert decoded.branch_instruction
    assert decoded.branch_condition == BranchCondition.ZERO
