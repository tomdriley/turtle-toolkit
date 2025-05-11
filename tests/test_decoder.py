import unittest
from simulator.modules.decoder import DecodeUnit
from simulator.modules.instruction_memory import InstructionBinary
from simulator.common.instruction_data import (
    ArithLogicFunction,
    BranchCondition,
)
from .binary_macros import (
    INSTRUCTION_NOP,
    INSTRUCTION_HALT,
)
from simulator.assembler import Assembler


class TestDecodeUnit(unittest.TestCase):
    def setUp(self):
        self.decoder = DecodeUnit("test_decoder")

    def test_decode_nop_instruction(self):
        # Example binary for NOP instruction
        binary_data = InstructionBinary(INSTRUCTION_NOP)
        decoded = self.decoder.decode(binary_data)
        self.assertTrue(decoded.nop_instruction)
        self.assertFalse(decoded.halt_instruction)

    def test_decode_halt_instruction(self):
        # Example binary for HALT instruction
        binary_data = InstructionBinary(INSTRUCTION_HALT)
        decoded = self.decoder.decode(binary_data)
        self.assertTrue(decoded.halt_instruction)
        self.assertFalse(decoded.nop_instruction)

    def test_decode_alu_instruction(self):
        # Example binary for ALU ADD instruction
        binary_data = InstructionBinary(Assembler.assemble("ADD R0"))
        decoded = self.decoder.decode(binary_data)
        self.assertTrue(decoded.alu_instruction)
        self.assertEqual(decoded.alu_function, ArithLogicFunction.ADD)

    def test_decode_branch_instruction(self):
        # Example binary for branch instruction with ZERO condition
        binary_data = InstructionBinary(Assembler.assemble("BZ 0x04"))
        decoded = self.decoder.decode(binary_data)
        self.assertTrue(decoded.branch_instruction)
        self.assertEqual(decoded.branch_condition, BranchCondition.ZERO)


if __name__ == "__main__":
    unittest.main()
