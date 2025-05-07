"""register_file.py - Register File module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto
from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import (
    DataBusValue,
    DataAddressBusValue,
    InstructionAddressBusValue,
)
from simulator.common.config import (
    DATA_WIDTH,
    INSTRUCTION_ADDRESS_WIDTH,
    DATA_ADDRESS_WIDTH,
)


@dataclass
class StatusRegisterValue:
    zero: bool
    positive: bool
    carry_set: bool
    signed_overflow_set: bool


class RegisterIndex(Enum):
    """Enum for register indices."""

    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    ACC = auto()
    DMAR = auto()
    DBAR = auto()
    DOFF = auto()
    IMAR = auto()
    IBAR = auto()
    IOFF = auto()
    STATUS = auto()


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
        }
    )
    status_register = StatusRegisterValue(True, True, False, False)
    data_memory_address = DataAddressBusValue(0)
    instruction_memory_address = InstructionAddressBusValue(0)
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
        if register_index == RegisterIndex.ACC:
            return self.get_acc_value()
        elif register_index == RegisterIndex.DOFF:
            data_full_address = self.get_dmar_value()
            data_offset = data_full_address.get_slice(0, DATA_WIDTH - 1)
            return DataBusValue(data_offset.unsigned_value())
        elif register_index == RegisterIndex.DBAR:
            data_full_address = self.get_dmar_value()
            data_bar = data_full_address.get_slice(DATA_WIDTH, DATA_ADDRESS_WIDTH - 1)
            return DataBusValue(data_bar.unsigned_value())
        elif register_index == RegisterIndex.IOFF:
            full_address = self.get_imar_value()
            offset = full_address.get_slice(0, DATA_WIDTH - 1)
            return DataBusValue(offset.unsigned_value())
        elif register_index == RegisterIndex.IBAR:
            full_address = self.get_imar_value()
            bar = full_address.get_slice(DATA_WIDTH, INSTRUCTION_ADDRESS_WIDTH - 1)
            return DataBusValue(bar.unsigned_value())
        elif register_index in self.state.registers:
            return self.state.registers[register_index]
        elif register_index == RegisterIndex.STATUS:
            return DataBusValue(
                (
                    self.state.status_register.zero << 0
                    | self.state.status_register.positive << 1
                    | self.state.status_register.carry_set << 2
                    | self.state.status_register.signed_overflow_set << 3
                )
            )
        elif register_index == RegisterIndex.DMAR:
            raise IndexError("DMAR can not be read in a single cycle.")
        elif register_index == RegisterIndex.IMAR:
            raise IndexError("IMAR can not be read in a single cycle.")
        else:
            raise IndexError(f"Register index {register_index} is not valid.")

    def get_dmar_value(self) -> DataAddressBusValue:
        """Get the value of the data memory address register."""
        return self.state.data_memory_address

    def get_imar_value(self) -> InstructionAddressBusValue:
        """Get the value of the instruction memory address register."""
        return self.state.instruction_memory_address

    def set_next_register_value(
        self, register_index: RegisterIndex, value: DataBusValue
    ) -> None:
        self.state.pending_register = register_index
        self.state.pending_value = value

    def get_status_register_value(self) -> StatusRegisterValue:
        """Get the value of the status register."""
        return self.state.status_register

    def set_next_status_register_value(
        self, signed_overflow: bool, carry_flag: bool
    ) -> None:
        self.state.pending_carry_flag = carry_flag
        self.state.pending_signed_overflow = signed_overflow

    def set_next_acc_value(self, value: DataBusValue) -> None:
        self.state.pending_accumulator = value

    def update_state(self) -> None:
        if self.state.pending_register is not None and self.state.pending_value is None:
            raise ValueError(
                f"Pending value for register {self.state.pending_register} is None."
            )
        data_addr_offset_mask = DataAddressBusValue(((1 << (DATA_WIDTH)) - 1))
        instr_addr_offset_mask = InstructionAddressBusValue(((1 << (DATA_WIDTH)) - 1))
        if (
            self.state.pending_register == RegisterIndex.DBAR
            and self.state.pending_value is not None
        ):
            self.state.data_memory_address = (
                (~data_addr_offset_mask)
                & DataAddressBusValue(
                    self.state.pending_value.unsigned_value() << DATA_WIDTH
                )
            ) | (data_addr_offset_mask & self.state.data_memory_address)
        elif (
            self.state.pending_register == RegisterIndex.DOFF
            and self.state.pending_value is not None
        ):
            self.state.data_memory_address = (
                (data_addr_offset_mask)
                & DataAddressBusValue(self.state.pending_value.unsigned_value())
            ) | (~data_addr_offset_mask & self.state.data_memory_address)
        elif (
            self.state.pending_register == RegisterIndex.IBAR
            and self.state.pending_value is not None
        ):
            self.state.instruction_memory_address = (
                (~instr_addr_offset_mask)
                & InstructionAddressBusValue(
                    self.state.pending_value.unsigned_value() << DATA_WIDTH
                )
            ) | (instr_addr_offset_mask & self.state.instruction_memory_address)
        elif (
            self.state.pending_register == RegisterIndex.IOFF
            and self.state.pending_value is not None
        ):
            self.state.instruction_memory_address = (
                (instr_addr_offset_mask)
                & InstructionAddressBusValue(self.state.pending_value.unsigned_value())
            ) | (~instr_addr_offset_mask & self.state.instruction_memory_address)
        elif self.state.pending_register == RegisterIndex.DMAR:
            raise IndexError("DMAR can not be written in a single cycle.")
        elif self.state.pending_register == RegisterIndex.IMAR:
            raise IndexError("IMAR can not be written in a single cycle.")
        elif self.state.pending_register == RegisterIndex.STATUS:
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
            self.state.pending_accumulator == 0
            if self.state.pending_accumulator
            else None
        )
        positive = (
            self.state.pending_accumulator.signed_value() >= 0
            if self.state.pending_accumulator
            else None
        )
        self.state.status_register = StatusRegisterValue(
            zero if zero is not None else self.state.status_register.zero,
            positive if positive is not None else self.state.status_register.positive,
            (
                self.state.pending_carry_flag
                if self.state.pending_carry_flag is not None
                else self.state.status_register.carry_set
            ),
            (
                self.state.pending_signed_overflow
                if self.state.pending_signed_overflow is not None
                else self.state.status_register.signed_overflow_set
            ),
        )
