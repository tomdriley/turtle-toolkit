import unittest
from simulator.modules.program_counter import ProgramCounter
from simulator.common.data_types import InstructionAddressBusValue
from simulator.modules.register_file import StatusRegisterValue
from simulator.modules.decoder import BranchCondition


class TestProgramCounter(unittest.TestCase):
    def setUp(self):
        self.program_counter = ProgramCounter("TestPC")

    def test_initialization(self):
        self.assertEqual(self.program_counter.get_current_instruction_address(), 0)

    def test_increment(self):
        self.program_counter.increment()
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 1)

    def test_jump_relative(self):
        # Test positive offset
        self.program_counter.jump_relative(InstructionAddressBusValue(5))
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 5)

        # Test negative offset
        self.program_counter.jump_relative(InstructionAddressBusValue(-3))
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 2)

    def test_jump_absolute(self):
        self.program_counter.jump_absolute(InstructionAddressBusValue(100))
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 100)

    def test_conditional_branch_zero_flag(self):
        # Test branch when zero flag is set
        status_reg = StatusRegisterValue(
            zero=True, positive=False, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.ZERO
        )
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 5)

        # Test no branch when zero flag is clear
        self.program_counter = ProgramCounter("TestPC")  # Reset PC
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.ZERO
        )
        self.program_counter.update_state()
        self.assertEqual(
            self.program_counter.get_current_instruction_address(), 1
        )  # Should increment instead

    def test_conditional_branch_positive_flag(self):
        # Test branch when positive flag is set
        status_reg = StatusRegisterValue(
            zero=False, positive=True, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.POSITIVE
        )
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 5)

        # Test no branch when positive flag is clear
        self.program_counter = ProgramCounter("TestPC")
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.POSITIVE
        )
        self.program_counter.update_state()
        self.assertEqual(
            self.program_counter.get_current_instruction_address(), 1
        )  # Should increment instead

    def test_conditional_branch_carry_flag(self):
        # Test branch when carry flag is set
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=True, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.CARRY_SET
        )
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 5)

        # Test no branch when carry flag is clear
        self.program_counter = ProgramCounter("TestPC")
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.CARRY_SET
        )
        self.program_counter.update_state()
        self.assertEqual(
            self.program_counter.get_current_instruction_address(), 1
        )  # Should increment instead

    def test_conditional_branch_overflow_flag(self):
        # Test branch when overflow flag is set
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=False, signed_overflow_set=True
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.OVERFLOW_SET
        )
        self.program_counter.update_state()
        self.assertEqual(self.program_counter.get_current_instruction_address(), 5)

        # Test no branch when overflow flag is clear
        self.program_counter = ProgramCounter("TestPC")
        status_reg = StatusRegisterValue(
            zero=False, positive=False, carry_set=False, signed_overflow_set=False
        )
        self.program_counter.conditionally_branch(
            status_reg, InstructionAddressBusValue(5), BranchCondition.OVERFLOW_SET
        )
        self.program_counter.update_state()
        self.assertEqual(
            self.program_counter.get_current_instruction_address(), 1
        )  # Should increment instead

    def test_update_state_without_next_value(self):
        with self.assertRaisesRegex(
            ValueError, "No next value set for program counter"
        ):
            self.program_counter.update_state()


if __name__ == "__main__":
    unittest.main()
