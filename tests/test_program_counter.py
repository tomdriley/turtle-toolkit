import pytest
from simulator.modules.program_counter import ProgramCounter
from simulator.common.data_types import InstructionAddressBusValue
from simulator.modules.register_file import StatusRegisterValue
from simulator.modules.decoder import BranchCondition


@pytest.fixture
def program_counter():
    return ProgramCounter("TestPC")


def test_initialization(program_counter):
    assert program_counter.get_current_instruction_address() == 0


def test_increment(program_counter):
    program_counter.increment()
    program_counter.update_state()
    assert program_counter.get_current_instruction_address() == 2


def test_jump_relative(program_counter):
    # Test positive offset
    program_counter.jump_relative(InstructionAddressBusValue(6))
    program_counter.update_state()
    assert program_counter.get_current_instruction_address() == 6

    # Test negative offset
    program_counter.jump_relative(InstructionAddressBusValue(-4))
    program_counter.update_state()
    assert program_counter.get_current_instruction_address() == 2


def test_jump_absolute(program_counter):
    program_counter.jump_absolute(InstructionAddressBusValue(100))
    program_counter.update_state()
    assert program_counter.get_current_instruction_address() == 100


def test_conditional_branch_zero_flag():
    # Test branch when zero flag is set
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=True, positive=False, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.ZERO
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 6

    # Test no branch when zero flag is clear
    pc = ProgramCounter("TestPC")  # Reset PC
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.ZERO
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 2  # Should increment instead


def test_conditional_branch_positive_flag():
    # Test branch when positive flag is set
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=True, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.POSITIVE
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 6

    # Test no branch when positive flag is clear
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.POSITIVE
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 2  # Should increment instead


def test_conditional_branch_carry_flag():
    # Test branch when carry flag is set
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=True, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.CARRY_SET
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 6

    # Test no branch when carry flag is clear
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.CARRY_SET
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 2  # Should increment instead


def test_conditional_branch_overflow_flag():
    # Test branch when overflow flag is set
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=True
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.OVERFLOW_SET
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 6

    # Test no branch when overflow flag is clear
    pc = ProgramCounter("TestPC")
    status_reg = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=False
    )
    pc.conditionally_branch(
        status_reg, InstructionAddressBusValue(6), BranchCondition.OVERFLOW_SET
    )
    pc.update_state()
    assert pc.get_current_instruction_address() == 2  # Should increment instead


def test_update_state_without_next_value():
    pc = ProgramCounter("TestPC")
    with pytest.raises(ValueError, match="No next value set for program counter"):
        pc.update_state()
