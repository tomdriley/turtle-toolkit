import unittest
from simulator.modules.alu import ALU, ArithLogicFunction
from simulator.common.data_types import DataBusValue


class TestALU(unittest.TestCase):

    def setUp(self):
        self.alu = ALU("ALU")

    def test_alu_addition(self):
        operand_a = DataBusValue(5)
        operand_b = DataBusValue(10)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

        self.assertEqual(outputs.result, DataBusValue(15))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_addition_with_zero(self):
        operand_a = DataBusValue(0)
        operand_b = DataBusValue(10)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

        self.assertEqual(outputs.result, DataBusValue(10))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_addition_with_negative(self):
        operand_a = DataBusValue(-5)
        operand_b = DataBusValue(10)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

        self.assertEqual(outputs.result, DataBusValue(5))
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_subtraction(self):
        operand_a = DataBusValue(10)
        operand_b = DataBusValue(5)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

        self.assertEqual(outputs.result, DataBusValue(5))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_subtraction_with_zero(self):
        operand_a = DataBusValue(10)
        operand_b = DataBusValue(0)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

        self.assertEqual(outputs.result, DataBusValue(10))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_subtraction_with_negative(self):
        operand_a = DataBusValue(-5)
        operand_b = DataBusValue(10)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

        self.assertEqual(outputs.result, DataBusValue(-15))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_subtraction_negative(self):
        operand_a = DataBusValue(5)
        operand_b = DataBusValue(10)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)

        self.assertEqual(outputs.result, DataBusValue(-5))
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_addition_with_overflow(self):
        # Max positive value for signed integer
        operand_a = DataBusValue(DataBusValue.max_signed_value())
        operand_b = DataBusValue(1)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)
        # Overflow wraps around
        self.assertEqual(outputs.result, DataBusValue(DataBusValue.min_signed_value()))
        self.assertFalse(outputs.carry_flag)
        self.assertTrue(outputs.signed_overflow)

    def test_alu_subtraction_with_underflow(self):
        operand_a = DataBusValue(DataBusValue.min_signed_value())
        operand_b = DataBusValue(1)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.SUB)
        # Underflow wraps around
        self.assertEqual(outputs.result, DataBusValue(DataBusValue.max_signed_value()))
        self.assertFalse(outputs.carry_flag)
        self.assertTrue(outputs.signed_overflow)

    def test_alu_addition_with_carry(self):
        # Max unsigned value
        operand_a = DataBusValue(DataBusValue.max_unsigned_value())
        operand_b = DataBusValue(1)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.ADD)

        self.assertEqual(outputs.result, DataBusValue(0))  # Carry wraps around to 0
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_and_operation(self):
        operand_a = DataBusValue(0b1100)
        operand_b = DataBusValue(0b1010)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.AND)

        self.assertEqual(outputs.result, DataBusValue(0b1000))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_or_operation(self):
        operand_a = DataBusValue(0b1100)
        operand_b = DataBusValue(0b1010)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.OR)

        self.assertEqual(outputs.result, DataBusValue(0b1110))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_xor_operation(self):
        operand_a = DataBusValue(0b1100)
        operand_b = DataBusValue(0b1010)
        outputs = self.alu.execute(operand_a, operand_b, ArithLogicFunction.XOR)

        self.assertEqual(outputs.result, DataBusValue(0b0110))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)

    def test_alu_invert_operation(self):
        operand_a = DataBusValue(0b1100)
        outputs = self.alu.execute(operand_a, DataBusValue(0), ArithLogicFunction.INV)

        self.assertEqual(
            outputs.result, DataBusValue(~0b1100 & DataBusValue.max_unsigned_value())
        )  # Mask to 32 bits
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
