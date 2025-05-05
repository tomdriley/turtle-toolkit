"""alu.py - Arithmetic Logic Unit (ALU) module
Author: Tom Riley
Date: 2025-05-04
"""

from enum import Enum, auto
from simulator.modules.base_module import BaseModule
from simulator.common.data_types import BusData
from simulator.common.logger import logger


class ALUOperation(Enum):
    """Enum for ALU operations."""

    ADD = auto()
    SUBTRACT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    INVERT = auto()
    BUFFER = auto()


class ALUOutputs:
    result: BusData = BusData(0)
    zero: bool = False
    signed_overflow: bool = False
    carry_flag: bool = False
    negative: bool = False


class ALU(BaseModule):
    def execute(
        self, operand_a: BusData, operand_b: BusData, function: ALUOperation
    ) -> ALUOutputs:
        """Execute the ALU operation based on the inputs."""
        logger.debug(f"Executing ALU with inputs: {operand_a}, {operand_b}, {function}")

        outputs = ALUOutputs()

        if function == ALUOperation.ADD:
            # Perform addition
            outputs.result = operand_a + operand_b
            # Carry flag is set if the result is greater than the max unsigned value
            outputs.carry_flag = (
                operand_a.unsigned_value() + operand_b.unsigned_value()
            ) >= BusData.max_unsigned_value()
            # Overflow occurs if the sign of the result is different from the sign of
            # both operands
            outputs.signed_overflow = (
                operand_a.is_negative() == operand_b.is_negative()
            ) and (outputs.result.is_negative() != operand_a.is_negative())
        elif function == ALUOperation.SUBTRACT:
            # Perform subtraction
            outputs.result = operand_a - operand_b
            # Carry flag is set if there is a borrow
            outputs.carry_flag = operand_a.unsigned_value() < operand_b.unsigned_value()
            # Overflow occurs if the sign of the result is different from the sign of
            # both operands
            outputs.signed_overflow = (
                operand_a.is_negative() != operand_b.is_negative()
            ) and (outputs.result.is_negative() != operand_a.is_negative())
        elif function == ALUOperation.AND:
            # Perform bitwise AND
            outputs.result = operand_a & operand_b
        elif function == ALUOperation.OR:
            # Perform bitwise OR
            outputs.result = operand_a | operand_b
        elif function == ALUOperation.XOR:
            # Perform bitwise XOR
            outputs.result = operand_a ^ operand_b
        elif function == ALUOperation.INVERT:
            # Perform bitwise NOT
            outputs.result = ~operand_a
        elif function == ALUOperation.BUFFER:
            # Buffer operation (no change)
            outputs.result = operand_a
        else:
            raise ValueError(f"Invalid ALU operation: {function}")
        # Set the zero flag if the result is zero
        outputs.zero = outputs.result.unsigned_value() == 0
        # Set the negative flag if the result is negative
        outputs.negative = outputs.result.is_negative()
        return outputs
