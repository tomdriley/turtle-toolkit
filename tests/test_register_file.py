import numpy as np
import pytest

from turtle_toolkit.common.data_types import (
    DataAddressBusValue,
    DataBusValue,
    InstructionAddressBusValue,
)
from turtle_toolkit.common.instruction_data import RegisterIndex
from turtle_toolkit.modules.register_file import RegisterFile, StatusRegisterValue


@pytest.fixture
def register_file() -> RegisterFile:
    return RegisterFile("RegisterFile")


def test_initial_state(register_file: RegisterFile) -> None:
    acc_value = register_file.get_acc_value()
    assert acc_value == DataBusValue(np.uint16(0))
    status_register_value = register_file.get_status_register_value()
    assert status_register_value.zero == (acc_value == 0)
    assert status_register_value.positive == (
        DataBusValue(acc_value).signed_value() >= 0
    )
    assert not status_register_value.carry_set
    assert not status_register_value.signed_overflow_set
    assert register_file.get_dmar_value() == DataBusValue(np.uint16(0))
    assert register_file.get_imar_value() == DataBusValue(np.uint16(0))
    for i in range(8):
        value = register_file.get_register_value(RegisterIndex(i))
        expected_value = DataBusValue(np.uint16(0))
        assert value == expected_value


def test_set_and_get_acc_value(register_file: RegisterFile) -> None:
    test_value = DataBusValue(np.uint16(123))
    # In the simulator, acc_next is set, then update_state() is called, then get_acc_value()
    # Replicating that logic here:
    register_file.set_next_acc_value(test_value)
    register_file.update_state()
    assert register_file.get_acc_value() == test_value


def test_set_and_get_register_value(register_file: RegisterFile) -> None:
    test_register = RegisterIndex(2)
    test_value = DataBusValue(np.uint16(45))
    # Similar to accumulator, next value is set, then state updated
    register_file.set_next_register_value(test_register, test_value)
    register_file.update_state()
    assert register_file.get_register_value(test_register) == test_value


def test_set_and_get_status_register_value(register_file: RegisterFile) -> None:
    test_signed_overflow = True
    test_carry_flag = False
    current_status = register_file.get_status_register_value()
    expected_status_value = StatusRegisterValue(
        zero=current_status.zero,
        positive=current_status.positive,
        carry_set=test_carry_flag,
        signed_overflow_set=test_signed_overflow,
    )

    register_file.set_next_status_register_value(
        np.bool_(test_signed_overflow), np.bool_(test_carry_flag)
    )
    register_file.update_state()
    assert register_file.get_status_register_value() == expected_status_value

    test_signed_overflow_2 = False
    test_carry_flag_2 = True
    expected_status_value_2 = StatusRegisterValue(
        zero=current_status.zero,
        positive=current_status.positive,
        carry_set=test_carry_flag_2,
        signed_overflow_set=test_signed_overflow_2,
    )

    register_file.set_next_status_register_value(
        np.bool_(test_signed_overflow_2), np.bool_(test_carry_flag_2)
    )
    register_file.update_state()
    assert register_file.get_status_register_value() == expected_status_value_2

    test_signed_overflow_3 = True
    test_carry_flag_3 = True
    expected_status_value_3 = StatusRegisterValue(
        zero=current_status.zero,
        positive=current_status.positive,
        carry_set=test_carry_flag_3,
        signed_overflow_set=test_signed_overflow_3,
    )

    register_file.set_next_status_register_value(
        np.bool_(test_signed_overflow_3), np.bool_(test_carry_flag_3)
    )
    register_file.update_state()
    assert register_file.get_status_register_value() == expected_status_value_3


def test_dmar_and_imar_mirror_registers(register_file: RegisterFile) -> None:
    # DMAR is Register 0, IMAR is Register 1
    dbar_val = DataBusValue(np.uint16(10))
    ibar_val = DataBusValue(np.uint16(15))

    register_file.set_next_register_value(RegisterIndex.DBAR, dbar_val)
    register_file.update_state()
    register_file.set_next_register_value(RegisterIndex.IBAR, ibar_val)
    register_file.update_state()

    assert register_file.get_dmar_value() == DataAddressBusValue(np.uint16(2560))
    assert register_file.get_imar_value() == InstructionAddressBusValue(np.uint16(3840))


def test_update_state_no_pending_changes(register_file: RegisterFile) -> None:
    # Set initial values
    acc_initial = DataBusValue(np.uint16(5))
    register_file.set_next_acc_value(acc_initial)
    register_file.update_state()
    assert register_file.get_acc_value() == acc_initial

    reg_idx = RegisterIndex(3)
    reg_val_initial = DataBusValue(np.uint16(15))
    register_file.set_next_register_value(reg_idx, reg_val_initial)
    register_file.update_state()
    assert register_file.get_register_value(reg_idx) == reg_val_initial

    # Call update_state again without setting any 'next' values
    register_file.update_state()

    # Verify values remain unchanged
    assert register_file.get_acc_value() == acc_initial
    assert register_file.get_register_value(reg_idx) == reg_val_initial
    # Status register also should not change if not explicitly set
    initial_status = register_file.get_status_register_value()
    register_file.update_state()
    assert register_file.get_status_register_value() == initial_status
