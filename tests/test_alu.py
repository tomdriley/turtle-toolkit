import numpy as np
import pytest

from turtle_toolkit.common.data_types import DataBusValue
from turtle_toolkit.modules.alu import ALU, ArithLogicFunction


@pytest.fixture
def alu():
    return ALU("ALU")


def test_alu_addition(alu):
    operand_a = DataBusValue(np.uint16(5))
    operand_b = DataBusValue(np.uint16(10))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

    assert outputs.result == DataBusValue(np.uint16(15))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_addition_with_zero(alu):
    operand_a = DataBusValue(np.uint16(0))
    operand_b = DataBusValue(np.uint16(10))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

    assert outputs.result == DataBusValue(np.uint16(10))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_addition_with_negative(alu):
    operand_a = DataBusValue(np.int16(-5))
    operand_b = DataBusValue(np.uint16(10))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

    assert outputs.result == DataBusValue(np.uint16(5))
    assert outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_subtraction(alu):
    operand_a = DataBusValue(np.uint16(10))
    operand_b = DataBusValue(np.uint16(5))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

    assert outputs.result == DataBusValue(np.uint16(5))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_subtraction_with_zero(alu):
    operand_a = DataBusValue(np.uint16(10))
    operand_b = DataBusValue(np.uint16(0))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

    assert outputs.result == DataBusValue(np.uint16(10))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_subtraction_with_negative(alu):
    operand_a = DataBusValue(np.int16(-5))
    operand_b = DataBusValue(np.uint16(10))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

    assert outputs.result == DataBusValue(np.int16(-15))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_subtraction_negative(alu):
    operand_a = DataBusValue(np.uint16(5))
    operand_b = DataBusValue(np.uint16(10))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

    assert outputs.result == DataBusValue(np.int16(-5))
    assert outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_addition_with_overflow(alu):
    # Max positive value for signed integer
    operand_a = DataBusValue(DataBusValue.MAX_SIGNED_VALUE)
    operand_b = DataBusValue(np.uint16(1))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)
    # Overflow wraps around
    assert outputs.result == DataBusValue(DataBusValue.MIN_SIGNED_VALUE)
    assert not outputs.carry_flag
    assert outputs.signed_overflow


def test_alu_subtraction_with_underflow(alu):
    operand_a = DataBusValue(DataBusValue.MIN_SIGNED_VALUE)
    operand_b = DataBusValue(np.uint16(1))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)
    # Underflow wraps around
    assert outputs.result == DataBusValue(DataBusValue.MAX_SIGNED_VALUE)
    assert not outputs.carry_flag
    assert outputs.signed_overflow


def test_alu_addition_with_carry(alu):
    # Max unsigned value
    operand_a = DataBusValue(DataBusValue.MAX_UNSIGNED_VALUE)
    operand_b = DataBusValue(np.uint16(1))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

    assert outputs.result == DataBusValue(np.uint16(0))  # Carry wraps around to 0
    assert outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_and_operation(alu):
    operand_a = DataBusValue(np.int16(0b1100))
    operand_b = DataBusValue(np.int16(0b1010))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.AND)

    assert outputs.result == DataBusValue(np.int16(0b1000))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_or_operation(alu):
    operand_a = DataBusValue(np.int16(0b1100))
    operand_b = DataBusValue(np.int16(0b1010))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.OR)

    assert outputs.result == DataBusValue(np.int16(0b1110))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_xor_operation(alu):
    operand_a = DataBusValue(np.int16(0b1100))
    operand_b = DataBusValue(np.int16(0b1010))
    outputs = alu.execute(operand_a, operand_b, ArithLogicFunction.XOR)

    assert outputs.result == DataBusValue(np.int16(0b0110))
    assert not outputs.carry_flag
    assert not outputs.signed_overflow


def test_alu_invert_operation(alu):
    operand_a = DataBusValue(np.int16(0b1100))
    outputs = alu.execute(operand_a, DataBusValue(np.uint16(0)), ArithLogicFunction.INV)

    assert outputs.result == DataBusValue(
        ~np.int16(0b1100) & DataBusValue.MAX_UNSIGNED_VALUE
    )  # Mask to 32 bits
    assert not outputs.carry_flag
    assert not outputs.signed_overflow
