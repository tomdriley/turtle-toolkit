"""register_file.py - Register File module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass, field
from typing import Optional

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
from turtle_toolkit.common.instruction_data import RegisterIndex
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
    registers: dict[RegisterIndex, DataBusValue] = field(
        default_factory=lambda: {
            RegisterIndex.R0: DataBusValue(0),
            RegisterIndex.R1: DataBusValue(0),
            RegisterIndex.R2: DataBusValue(0),
            RegisterIndex.R3: DataBusValue(0),
            RegisterIndex.R4: DataBusValue(0),
            RegisterIndex.R5: DataBusValue(0),
            RegisterIndex.R6: DataBusValue(0),
            RegisterIndex.R7: DataBusValue(0),
            RegisterIndex.ACC: DataBusValue(0),
            RegisterIndex.DBAR: DataBusValue(0),
            RegisterIndex.DOFF: DataBusValue(0),
            RegisterIndex.IBAR: DataBusValue(0),
            RegisterIndex.IOFF: DataBusValue(0),
            RegisterIndex.STATUS: DataBusValue(3),
        }
    )
    pending_register: Optional[RegisterIndex] = None
    pending_value: Optional[DataBusValue] = None
    pending_carry_flag: Optional[bool] = None
    pending_signed_overflow: Optional[bool] = None
    pending_accumulator: Optional[DataBusValue] = None


class RegisterFile(BaseModule):
    def __init__(self, name: str):
        self.state = RegisterFileState()
        super().__init__(name, self.state)

    def get_acc_value(self):
        """Get the value of the accumulator register."""
        return self.state.registers[RegisterIndex.ACC]

    def get_register_value(self, register_index: RegisterIndex) -> DataBusValue:
        if register_index in self.state.registers:
            return self.state.registers[register_index]
        else:
            raise IndexError(f"Register index {register_index} is not valid.")

    def get_dmar_value(self) -> DataAddressBusValue:
        """Get the value of the data memory address register."""
        return DataAddressBusValue(
            (
                (
                    self.state.registers[RegisterIndex.DBAR].unsigned_value()
                    & ((1 << (DATA_ADDRESS_WIDTH - DATA_WIDTH)) - 1)
                )
                << DATA_WIDTH
            )
            | self.state.registers[RegisterIndex.DOFF].unsigned_value()
        )

    def get_imar_value(self) -> InstructionAddressBusValue:
        """Get the value of the instruction memory address register."""
        return InstructionAddressBusValue(
            (
                (
                    self.state.registers[RegisterIndex.IBAR].unsigned_value()
                    & ((1 << (INSTRUCTION_ADDRESS_WIDTH - DATA_WIDTH)) - 1)
                )
                << DATA_WIDTH
            )
            | self.state.registers[RegisterIndex.IOFF].unsigned_value()
        )

    def set_next_register_value(
        self, register_index: RegisterIndex, value: DataBusValue
    ) -> None:
        self.state.pending_register = register_index
        self.state.pending_value = value

    def get_status_register_value(self) -> StatusRegisterValue:
        """Get the value of the status register."""
        status_value = self.state.registers[RegisterIndex.STATUS].unsigned_value()
        return StatusRegisterValue(
            zero=(status_value >> 0) & 1 == 1,
            positive=(status_value >> 1) & 1 == 1,
            carry_set=(status_value >> 2) & 1 == 1,
            signed_overflow_set=(status_value >> 3) & 1 == 1,
        )

    def set_next_status_register_value(
        self, signed_overflow: bool, carry_flag: bool
    ) -> None:
        assert isinstance(signed_overflow, bool)
        assert isinstance(carry_flag, bool)
        self.state.pending_carry_flag = carry_flag
        self.state.pending_signed_overflow = signed_overflow

    def set_next_acc_value(self, value: DataBusValue) -> None:
        self.state.pending_accumulator = value

    def update_state(self) -> None:
        if self.state.pending_register is not None and self.state.pending_value is None:
            raise ValueError(
                f"Pending value for register {self.state.pending_register} is None."
            )
        if self.state.pending_register == RegisterIndex.STATUS:
            raise IndexError("STATUS can not be written directly")
        elif self.state.pending_register == RegisterIndex.ACC:
            raise IndexError("ACC can not be written directly")
        elif (
            self.state.pending_register in self.state.registers
            and self.state.pending_value is not None
        ):
            self.state.registers[self.state.pending_register] = self.state.pending_value
        elif self.state.pending_register is not None:
            raise IndexError(
                f"Register index {self.state.pending_register} is not valid."
            )
        self.state.pending_register = None
        self.state.pending_value = None
        if self.state.pending_accumulator is not None:
            self.state.registers[RegisterIndex.ACC] = self.state.pending_accumulator
        zero = (
            (self.state.pending_accumulator.unsigned_value() == 0)
            if self.state.pending_accumulator
            else None
        )
        positive = (
            (self.state.pending_accumulator.signed_value() >= 0)
            if self.state.pending_accumulator
            else None
        )

        def resolve_next_bit(current_bit: int, pending_bit: Optional[bool]) -> int:
            """Resolve the next bit value."""
            return int(pending_bit) if pending_bit is not None else current_bit

        def compute_next_status_bit(shift: int, pending: Optional[bool]) -> int:
            """Compute the next status bit."""
            current_bit = (current_status_value >> shift) & 1
            return resolve_next_bit(current_bit, pending) << shift

        # Extract the current status register value
        current_status_value = self.state.registers[
            RegisterIndex.STATUS
        ].unsigned_value()

        # Compute the next status register value
        next_status_value = 0
        next_status_value |= compute_next_status_bit(0, zero)
        next_status_value |= compute_next_status_bit(1, positive)
        next_status_value |= compute_next_status_bit(2, self.state.pending_carry_flag)
        next_status_value |= compute_next_status_bit(
            3, self.state.pending_signed_overflow
        )

        # Update the STATUS register with the computed value
        self.state.registers[RegisterIndex.STATUS] = DataBusValue(next_status_value)
