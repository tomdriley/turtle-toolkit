import numpy as np

from turtle_toolkit.common.config import INSTRUCTION_WIDTH
from turtle_toolkit.common.data_types import DataBusValue
from turtle_toolkit.common.instruction_data import BranchCondition
from turtle_toolkit.modules.program_counter import ProgramCounter
from turtle_toolkit.modules.register_file import StatusRegisterValue


def test_branch_negative_condition() -> None:
    """Test the BN (Branch if Negative) condition."""
    pc = ProgramCounter("TestPC")

    # Simulate a negative value in the accumulator
    status_register = StatusRegisterValue(
        zero=False, positive=False, carry_set=False, signed_overflow_set=False
    )

    # Set an offset for the branch
    offset = DataBusValue(np.uint16(INSTRUCTION_WIDTH // 8))

    # Perform the conditional branch
    pc.conditionally_branch(status_register, offset, BranchCondition.NEGATIVE)

    # Verify that the program counter jumped to the correct address
    assert pc.state.next_value == pc.state.value + offset


def test_branch_positive_condition() -> None:
    """Test the BP (Branch if Positive) condition."""
    pc = ProgramCounter("TestPC")

    # Simulate a positive value in the accumulator
    status_register = StatusRegisterValue(
        zero=False, positive=True, carry_set=False, signed_overflow_set=False
    )

    # Set an offset for the branch
    offset = DataBusValue(np.uint16(INSTRUCTION_WIDTH // 8))

    # Perform the conditional branch
    pc.conditionally_branch(status_register, offset, BranchCondition.POSITIVE)

    # Verify that the program counter jumped to the correct address
    assert pc.state.next_value == pc.state.value + offset


def test_branch_zero_condition() -> None:
    """Test the BZ (Branch if Zero) condition."""
    pc = ProgramCounter("TestPC")

    # Simulate a zero value in the accumulator
    status_register = StatusRegisterValue(
        zero=True, positive=False, carry_set=False, signed_overflow_set=False
    )

    # Set an offset for the branch
    offset = DataBusValue(np.uint16(INSTRUCTION_WIDTH // 8))

    # Perform the conditional branch
    pc.conditionally_branch(status_register, offset, BranchCondition.ZERO)

    # Verify that the program counter jumped to the correct address
    assert pc.state.next_value == pc.state.value + offset
