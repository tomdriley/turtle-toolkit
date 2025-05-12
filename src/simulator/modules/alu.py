"""alu.py - Arithmetic Logic Unit (ALU) module
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Optional

from simulator.modules.base_module import BaseModule
from simulator.common.data_types import DataBusValue
from simulator.common.logger import logger
from simulator.common.instruction_data import ArithLogicFunction


class ALUOutputs:
    result: DataBusValue = DataBusValue(0)
    signed_overflow: bool = False
    carry_flag: bool = False


class ALU(BaseModule):
    def execute(
        self,
        operand_a: DataBusValue,
        operand_b: DataBusValue,
        function: Optional[ArithLogicFunction],
    ) -> ALUOutputs:
        """Execute the ALU operation based on the inputs."""
        logger.debug(f"Executing ALU with inputs: {operand_a}, {operand_b}, {function}")

        outputs = ALUOutputs()

        if function is None:
            raise ValueError("ALU function cannot be None")

        if function == ArithLogicFunction.ADD:
            # Perform addition
            outputs.result = operand_a + operand_b
            # Carry flag is set if the result is greater than the max unsigned value
            outputs.carry_flag = (
                operand_a.unsigned_value() + operand_b.unsigned_value()
            ) > DataBusValue.max_unsigned_value()
            # Overflow occurs if the sign of the result is different from the sign of
            # both operands
            outputs.signed_overflow = (
                operand_a.is_negative() == operand_b.is_negative()
            ) and (outputs.result.is_negative() != operand_a.is_negative())
        elif function == ArithLogicFunction.SUB:
            # Perform subtraction
            outputs.result = operand_a - operand_b
            # Carry flag is set if there is a borrow
            outputs.carry_flag = operand_a.unsigned_value() < operand_b.unsigned_value()
            # Overflow occurs if the sign of the result is different from the sign of
            # both operands
            outputs.signed_overflow = (
                operand_a.is_negative() != operand_b.is_negative()
            ) and (outputs.result.is_negative() != operand_a.is_negative())
        elif function == ArithLogicFunction.AND:
            # Perform bitwise AND
            outputs.result = operand_a & operand_b
        elif function == ArithLogicFunction.OR:
            # Perform bitwise OR
            outputs.result = operand_a | operand_b
        elif function == ArithLogicFunction.XOR:
            # Perform bitwise XOR
            outputs.result = operand_a ^ operand_b
        elif function == ArithLogicFunction.INV:
            # Perform bitwise NOT
            outputs.result = ~operand_a
        else:
            raise ValueError(f"Invalid ALU operation: {function}")
        return outputs
