import unittest

from simulator.modules.register_file import (
    RegisterFile,
    RegisterIndex,
    StatusRegisterValue,
)
from simulator.common.data_types import (
    DataBusValue,
    DataAddressBusValue,
    InstructionAddressBusValue,
)


class TestRegisterFile(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile("RegisterFile")

    def test_initial_state(self):
        acc_value = self.register_file.get_acc_value()
        self.assertEqual(acc_value, DataBusValue(0))
        status_register_value = self.register_file.get_status_register_value()
        self.assertEqual(status_register_value.zero, acc_value == 0)
        self.assertEqual(status_register_value.positive, acc_value.signed_value() >= 0)
        self.assertEqual(status_register_value.carry_set, False)
        self.assertEqual(status_register_value.signed_overflow_set, False)
        self.assertEqual(self.register_file.get_dmar_value(), DataBusValue(0))
        self.assertEqual(self.register_file.get_imar_value(), DataBusValue(0))
        for i in range(8):
            value = self.register_file.get_register_value(RegisterIndex(i))
            expected_value = DataBusValue(0)
            self.assertEqual(value, expected_value)

    def test_set_and_get_acc_value(self):
        test_value = DataBusValue(123)
        # In the simulator, acc_next is set, then update_state() is called, then get_acc_value()
        # Replicating that logic here:
        self.register_file.set_next_acc_value(test_value)
        self.register_file.update_state()
        self.assertEqual(self.register_file.get_acc_value(), test_value)

    def test_set_and_get_register_value(self):
        test_register = RegisterIndex(2)
        test_value = DataBusValue(45)
        # Similar to accumulator, next value is set, then state updated
        self.register_file.set_next_register_value(test_register, test_value)
        self.register_file.update_state()
        self.assertEqual(
            self.register_file.get_register_value(test_register), test_value
        )

    def test_set_and_get_status_register_value(self):
        test_signed_overflow = DataBusValue(1)
        test_carry_flag = DataBusValue(0)
        current_status = self.register_file.get_status_register_value()
        expected_status_value = StatusRegisterValue(
            zero=current_status.zero,
            positive=current_status.positive,
            carry_set=test_carry_flag,
            signed_overflow_set=test_signed_overflow,
        )

        self.register_file.set_next_status_register_value(
            test_signed_overflow, test_carry_flag
        )
        self.register_file.update_state()
        self.assertEqual(
            self.register_file.get_status_register_value(), expected_status_value
        )

        test_signed_overflow_2 = DataBusValue(0)
        test_carry_flag_2 = DataBusValue(1)
        expected_status_value_2 = StatusRegisterValue(
            zero=current_status.zero,
            positive=current_status.positive,
            carry_set=test_carry_flag_2,
            signed_overflow_set=test_signed_overflow_2,
        )

        self.register_file.set_next_status_register_value(
            test_signed_overflow_2, test_carry_flag_2
        )
        self.register_file.update_state()
        self.assertEqual(
            self.register_file.get_status_register_value(), expected_status_value_2
        )

        test_signed_overflow_3 = DataBusValue(1)
        test_carry_flag_3 = DataBusValue(1)
        expected_status_value_3 = StatusRegisterValue(
            zero=current_status.zero,
            positive=current_status.positive,
            carry_set=test_carry_flag_3,
            signed_overflow_set=test_signed_overflow_3,
        )

        self.register_file.set_next_status_register_value(
            test_signed_overflow_3, test_carry_flag_3
        )
        self.register_file.update_state()
        self.assertEqual(
            self.register_file.get_status_register_value(), expected_status_value_3
        )

    def test_dmar_and_imar_mirror_registers(self):
        # DMAR is Register 0, IMAR is Register 1
        dbar_val = DataBusValue(10)
        ibar_val = DataBusValue(15)

        self.register_file.set_next_register_value(RegisterIndex.DBAR, dbar_val)
        self.register_file.update_state()
        self.register_file.set_next_register_value(RegisterIndex.IBAR, ibar_val)
        self.register_file.update_state()

        self.assertEqual(self.register_file.get_dmar_value(), DataAddressBusValue(2560))
        self.assertEqual(
            self.register_file.get_imar_value(), InstructionAddressBusValue(3840)
        )

    def test_update_state_no_pending_changes(self):
        # Set initial values
        acc_initial = DataBusValue(5)
        self.register_file.set_next_acc_value(acc_initial)
        self.register_file.update_state()
        self.assertEqual(self.register_file.get_acc_value(), acc_initial)

        reg_idx = RegisterIndex(3)
        reg_val_initial = DataBusValue(15)
        self.register_file.set_next_register_value(reg_idx, reg_val_initial)
        self.register_file.update_state()
        self.assertEqual(
            self.register_file.get_register_value(reg_idx), reg_val_initial
        )

        # Call update_state again without setting any 'next' values
        self.register_file.update_state()

        # Verify values remain unchanged
        self.assertEqual(self.register_file.get_acc_value(), acc_initial)
        self.assertEqual(
            self.register_file.get_register_value(reg_idx), reg_val_initial
        )
        # Status register also should not change if not explicitly set
        initial_status = self.register_file.get_status_register_value()
        self.register_file.update_state()
        self.assertEqual(self.register_file.get_status_register_value(), initial_status)
