"""program_counter.py - Program Counter module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import InstructionAddressBusValue
from simulator.modules.register_file import StatusRegisterValue
from simulator.modules.decoder import BranchCondition


class ProgramCounterState(BaseModuleState):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.next_value = 0


class ProgramCounter(BaseModule):
    def __init__(self, name: str):
        self.state = ProgramCounterState()
        super().__init__(name, self.state)

    def increment(self):
        """Increment the program counter."""
        self.state.next_value += 1

    def jump_relative(self, offset: InstructionAddressBusValue):
        """Set the program counter to a specific value."""
        self.state.next_value = self.state.value + offset.signed_value()

    def jump_absolute(self, address: InstructionAddressBusValue):
        """Set the program counter to a specific value."""
        self.state.next_value = address.unsigned_value()

    def conditionally_branch(
        self,
        status_register: StatusRegisterValue,
        offset: InstructionAddressBusValue,
        branch_condition: BranchCondition,
    ):
        raise NotImplementedError()

    def get_current_instruction_address(self):
        """Get the current instruction address."""
        return self.state.value

    def update_state(self) -> None:
        raise NotImplementedError()
