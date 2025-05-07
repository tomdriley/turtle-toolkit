"""register_file.py - Register File module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import (
    DataBusValue,
    DataAddressBusValue,
    InstructionAddressBusValue,
)


@dataclass
class StatusRegisterValue:
    zero: bool
    positive: bool
    carry_set: bool
    signed_overflow_set: bool


class RegisterIndex:
    pass


class RegisterFileState(BaseModuleState):
    pass


class RegisterFile(BaseModule):
    def __init__(self, name: str):
        self.state = RegisterFileState()
        super().__init__(name, self.state)

    def get_acc_value(self):
        raise NotImplementedError()

    def get_register_value(self, register_index: RegisterIndex) -> DataBusValue:
        raise NotImplementedError()

    def get_dmar_value(self) -> DataAddressBusValue:
        raise NotImplementedError()

    def get_imar_value(self) -> InstructionAddressBusValue:
        raise NotImplementedError()

    def set_next_register_value(
        self, register_index: RegisterIndex, value: DataBusValue
    ) -> None:
        raise NotImplementedError()

    def get_status_register_value(self) -> StatusRegisterValue:
        raise NotImplementedError()

    def set_next_status_register_value(
        self, signed_overflow: bool, carry_flag: bool
    ) -> None:
        raise NotImplementedError()

    def set_next_acc_value(self, value: DataBusValue) -> None:
        raise NotImplementedError()

    def update_state(self) -> None:
        raise NotImplementedError()
