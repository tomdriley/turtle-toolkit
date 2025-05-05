import unittest
from simulator.modules.alu import ALU, ALUOperation
from simulator.common.data_types import BusData


class TestALU(unittest.TestCase):

    def test_alu_addition(self):
        alu = ALU("ALU")
        operand_a = BusData(5)
        operand_b = BusData(10)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.ADD)

        self.assertEqual(outputs.result, BusData(15))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_addition_with_zero(self):
        alu = ALU("ALU")
        operand_a = BusData(0)
        operand_b = BusData(10)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.ADD)

        self.assertEqual(outputs.result, BusData(10))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_addition_with_negative(self):
        alu = ALU("ALU")
        operand_a = BusData(-5)
        operand_b = BusData(10)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.ADD)

        self.assertEqual(outputs.result, BusData(5))
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_subtraction(self):
        alu = ALU("ALU")
        operand_a = BusData(10)
        operand_b = BusData(5)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.SUBTRACT)

        self.assertEqual(outputs.result, BusData(5))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_subtraction_with_zero(self):
        alu = ALU("ALU")
        operand_a = BusData(10)
        operand_b = BusData(0)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.SUBTRACT)

        self.assertEqual(outputs.result, BusData(10))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_subtraction_with_negative(self):
        alu = ALU("ALU")
        operand_a = BusData(-5)
        operand_b = BusData(10)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.SUBTRACT)

        self.assertEqual(outputs.result, BusData(-15))
        self.assertFalse(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertTrue(outputs.negative)

    def test_alu_subtraction_negative(self):
        alu = ALU("ALU")
        operand_a = BusData(5)
        operand_b = BusData(10)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.SUBTRACT)

        self.assertEqual(outputs.result, BusData(-5))
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertTrue(outputs.negative)

    def test_alu_addition_with_overflow(self):
        alu = ALU("ALU")
        # Max positive value for signed integer
        operand_a = BusData(BusData.max_signed_value())
        operand_b = BusData(1)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.ADD)
        # Overflow wraps around
        self.assertEqual(outputs.result, BusData(BusData.min_signed_value()))
        self.assertFalse(outputs.carry_flag)
        self.assertTrue(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertTrue(outputs.negative)

    def test_alu_subtraction_with_underflow(self):
        alu = ALU("ALU")
        operand_a = BusData(BusData.min_signed_value())
        operand_b = BusData(1)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.SUBTRACT)
        # Underflow wraps around

        self.assertEqual(outputs.result, BusData(BusData.max_signed_value()))
        self.assertFalse(outputs.carry_flag)
        self.assertTrue(outputs.signed_overflow)
        self.assertFalse(outputs.zero)
        self.assertFalse(outputs.negative)

    def test_alu_addition_with_carry(self):
        alu = ALU("ALU")
        # Max unsigned value
        operand_a = BusData(BusData.max_unsigned_value())
        operand_b = BusData(1)
        outputs = alu.execute(operand_a, operand_b, ALUOperation.ADD)

        self.assertEqual(outputs.result, BusData(0))  # Carry wraps around to 0
        self.assertTrue(outputs.carry_flag)
        self.assertFalse(outputs.signed_overflow)
        self.assertTrue(outputs.zero)
        self.assertFalse(outputs.negative)


if __name__ == "__main__":
    unittest.main()
