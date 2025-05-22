"""register_file.py - Register File module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from line_profiler import profile

from turtle_toolkit.common.config import (
    DATA_ADDRESS_WIDTH,
    DATA_WIDTH,
    INSTRUCTION_ADDRESS_WIDTH,
)
from turtle_toolkit.common.data_types import (
    DataAddressBusValue,
    DataBusValue,
    InstructionAddressBusValue,
)
from turtle_toolkit.common.instruction_data import MAX_REGISTER_INDEX, RegisterIndex
from turtle_toolkit.modules.base_module import BaseModule, BaseModuleState


@dataclass
class StatusRegisterValue:
    zero: bool
    positive: bool
    carry_set: bool
    signed_overflow_set: bool


@dataclass
class RegisterFileState(BaseModuleState):
    """State of the Register File."""

    # Register values
    registers: np.ndarray = field(
        default_factory=lambda: (
            lambda arr: (
                arr.__setitem__(RegisterIndex.STATUS.value, np.uint16(3)),
                arr,
            )[1]
        )(np.zeros(MAX_REGISTER_INDEX + 1, dtype=np.uint16))
    )
    pending_register: Optional[RegisterIndex] = None
    pending_value: Optional[np.uint16] = None
    pending_carry_flag: Optional[np.bool] = None
    pending_signed_overflow: Optional[np.bool] = None
    pending_accumulator: Optional[np.uint16] = None


class RegisterFile(BaseModule):
    def __init__(self, name: str):
        self.state = RegisterFileState()
        super().__init__(name, self.state)

    def get_acc_value(self):
        """Get the value of the accumulator register."""
        return self.state.registers[RegisterIndex.ACC.value]

    def get_register_value(self, register_index: RegisterIndex) -> DataBusValue:
        return DataBusValue(self.state.registers[register_index.value])

    def get_dmar_value(self) -> DataAddressBusValue:
        """Get the value of the data memory address register."""
        return DataAddressBusValue(
            (
                (
                    self.state.registers[RegisterIndex.DBAR.value]
                    & ((1 << (DATA_ADDRESS_WIDTH - DATA_WIDTH)) - 1)
                )
                << DATA_WIDTH
            )
            | (self.state.registers[RegisterIndex.DOFF.value] & ((1 << DATA_WIDTH) - 1))
        )

    def get_imar_value(self) -> InstructionAddressBusValue:
        """Get the value of the instruction memory address register."""
        return InstructionAddressBusValue(
            (
                (
                    self.state.registers[RegisterIndex.IBAR.value]
                    & ((1 << (INSTRUCTION_ADDRESS_WIDTH - DATA_WIDTH)) - 1)
                )
                << DATA_WIDTH
            )
            | (self.state.registers[RegisterIndex.IOFF.value] & ((1 << DATA_WIDTH) - 1))
        )

    def set_next_register_value(
        self, register_index: RegisterIndex, value: DataBusValue
    ) -> None:
        self.state.pending_register = register_index
        self.state.pending_value = np.uint16(value.value)

    def get_status_register_value(self) -> StatusRegisterValue:
        """Get the value of the status register."""
        status_value = self.state.registers[RegisterIndex.STATUS.value]
        return StatusRegisterValue(
            zero=(status_value >> 0) & 1 == 1,
            positive=(status_value >> 1) & 1 == 1,
            carry_set=(status_value >> 2) & 1 == 1,
            signed_overflow_set=(status_value >> 3) & 1 == 1,
        )

    def set_next_status_register_value(
        self, signed_overflow: np.bool, carry_flag: np.bool
    ) -> None:
        assert isinstance(signed_overflow, np.bool)
        assert isinstance(carry_flag, np.bool)
        self.state.pending_carry_flag = carry_flag
        self.state.pending_signed_overflow = signed_overflow

    def set_next_acc_value(self, value: DataBusValue) -> None:
        self.state.pending_accumulator = np.uint16(value.value)

    @profile
    def update_state(self) -> None:
        if self.state.pending_register is not None and self.state.pending_value is None:
            raise ValueError(
                f"Pending value for register {self.state.pending_register} is None."
            )
        if self.state.pending_register == RegisterIndex.STATUS:
            raise IndexError("STATUS can not be written directly")
        elif self.state.pending_register == RegisterIndex.ACC:
            raise IndexError("ACC can not be written directly")
        if (
            self.state.pending_value is not None
            and self.state.pending_register is not None
        ):
            self.state.registers[self.state.pending_register.value] = (
                self.state.pending_value
            )
        self.state.pending_register = None
        self.state.pending_value = None
        if self.state.pending_accumulator is not None:
            self.state.registers[RegisterIndex.ACC.value] = (
                self.state.pending_accumulator
            )
        zero = (
            (self.state.pending_accumulator == 0)
            if self.state.pending_accumulator
            else None
        )
        positive = (
            (DataBusValue(self.state.pending_accumulator).signed_value() >= 0)
            if self.state.pending_accumulator
            else None
        )

        def resolve_next_bit(
            current_bit: np.uint16, pending_bit: Optional[np.bool]
        ) -> np.uint16:
            """Resolve the next bit value."""
            return np.uint16(pending_bit) if pending_bit is not None else current_bit

        def compute_next_status_bit(
            shift: np.uint16, pending: Optional[np.bool]
        ) -> np.uint16:
            """Compute the next status bit."""
            current_bit = (current_status_value >> shift) & 1
            return resolve_next_bit(current_bit, pending) << shift

        # Extract the current status register value
        current_status_value = self.state.registers[RegisterIndex.STATUS.value]

        # Compute the next status register value
        next_status_value = np.uint16(0)
        next_status_value |= compute_next_status_bit(np.uint16(0), zero)
        next_status_value |= compute_next_status_bit(np.uint16(1), positive)
        next_status_value |= compute_next_status_bit(
            np.uint16(2), self.state.pending_carry_flag
        )
        next_status_value |= compute_next_status_bit(
            np.uint16(3), self.state.pending_signed_overflow
        )

        # Update the STATUS register with the computed value
        self.state.registers[RegisterIndex.STATUS.value] = next_status_value
