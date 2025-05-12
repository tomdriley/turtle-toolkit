import unittest
from simulator.assembler import Assembler
from simulator.modules.register_file import RegisterIndex
from simulator.modules.alu import ArithLogicFunction
from simulator.modules.decoder import BranchCondition
from simulator.assembler import Opcode, RegMemoryFunction
from simulator.common.data_types import DataBusValue, InstructionAddressBusValue
from .binary_macros import (
    INSTRUCTION_NOP,
    INSTRUCTION_HALT,
)


class TestAssembler(unittest.TestCase):
    def test_parse_assembly(self):
        source = """
        START: ADD R0
        SUBI 0x10
        JMP
        END: INV
        """
        instructions, labels = Assembler.parse_assembly(source)

        self.assertEqual(labels, {"START": 0, "END": 6})
        self.assertEqual(len(instructions), 4)

        self.assertEqual(instructions[0].opcode, Opcode.ARITH_LOGIC)
        self.assertEqual(instructions[0].function, ArithLogicFunction.ADD)
        self.assertEqual(instructions[0].register, RegisterIndex.R0)

        self.assertEqual(instructions[1].opcode, Opcode.ARITH_LOGIC_IMM)
        self.assertEqual(instructions[1].function, ArithLogicFunction.SUB)
        self.assertEqual(instructions[1].data_immediate, 0x10)

        self.assertEqual(instructions[2].opcode, Opcode.JUMP_REG)

        self.assertEqual(instructions[3].opcode, Opcode.ARITH_LOGIC)
        self.assertEqual(instructions[3].function, ArithLogicFunction.INV)

    def test_parse_branch_instructions(self):
        source = """
        BZ 0x04
        BNZ 0x08
        BP 0x0C
        BN 0x10
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 4)

        self.assertTrue(instructions[0].conditional_branch)
        self.assertEqual(instructions[0].branch_conditon, BranchCondition.ZERO)
        self.assertEqual(
            instructions[0].address_immediate, InstructionAddressBusValue(0x04)
        )

        self.assertTrue(instructions[1].conditional_branch)
        self.assertEqual(instructions[1].branch_conditon, BranchCondition.NOT_ZERO)
        self.assertEqual(
            instructions[1].address_immediate, InstructionAddressBusValue(0x08)
        )

        self.assertTrue(instructions[2].conditional_branch)
        self.assertEqual(instructions[2].branch_conditon, BranchCondition.POSITIVE)
        self.assertEqual(
            instructions[2].address_immediate, InstructionAddressBusValue(0x0C)
        )

        self.assertTrue(instructions[3].conditional_branch)
        self.assertEqual(instructions[3].branch_conditon, BranchCondition.NEGATIVE)
        self.assertEqual(
            instructions[3].address_immediate, InstructionAddressBusValue(0x10)
        )

    def test_invalid_syntax(self):
        with self.assertRaises(SyntaxError):
            Assembler.parse_assembly("INVALID INSTRUCTION")

    def test_memory_instructions(self):
        source = """
        LOAD
        STORE
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 2)

        self.assertEqual(instructions[0].opcode, Opcode.REG_MEMORY)
        self.assertEqual(instructions[0].function, RegMemoryFunction.LOAD)

        self.assertEqual(instructions[1].opcode, Opcode.REG_MEMORY)
        self.assertEqual(instructions[1].function, RegMemoryFunction.STORE)

    def test_immediate_values(self):
        source = """
        ADDI 0xFF
        SUBI 0b1010
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 2)

        self.assertEqual(instructions[0].opcode, Opcode.ARITH_LOGIC_IMM)
        self.assertEqual(instructions[0].function, ArithLogicFunction.ADD)
        self.assertEqual(instructions[0].data_immediate, DataBusValue(0xFF))

        self.assertEqual(instructions[1].opcode, Opcode.ARITH_LOGIC_IMM)
        self.assertEqual(instructions[1].function, ArithLogicFunction.SUB)
        self.assertEqual(instructions[1].data_immediate, DataBusValue(0b1010))

    def test_nop(self):
        source = """
        ADDI 0
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].opcode, Opcode.ARITH_LOGIC_IMM)
        self.assertEqual(instructions[0].function, ArithLogicFunction.ADD)
        self.assertEqual(instructions[0].data_immediate, DataBusValue(0x00))

        binary = Assembler.encode_instruction(instructions[0])
        self.assertEqual(binary, INSTRUCTION_NOP)

    def test_halt(self):
        source = """
        JMPI 0
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].opcode, Opcode.JUMP_IMM)
        self.assertEqual(
            instructions[0].address_immediate, InstructionAddressBusValue(0)
        )

        binary = Assembler.encode_instruction(instructions[0])
        self.assertEqual(binary, INSTRUCTION_HALT)

    def test_nop_macro(self):
        source = """
        NOP
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].opcode, Opcode.ARITH_LOGIC_IMM)
        self.assertEqual(instructions[0].function, ArithLogicFunction.ADD)
        self.assertEqual(instructions[0].data_immediate, DataBusValue(0x00))

        binary = Assembler.encode_instruction(instructions[0])
        self.assertEqual(binary, INSTRUCTION_NOP)

    def test_halt_macro(self):
        source = """
        HALT
        """
        instructions, _ = Assembler.parse_assembly(source)

        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].opcode, Opcode.JUMP_IMM)
        self.assertEqual(
            instructions[0].address_immediate, InstructionAddressBusValue(0)
        )

        binary = Assembler.encode_instruction(instructions[0])
        self.assertEqual(binary, INSTRUCTION_HALT)
