"""program_counter.py - Program Counter module
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Optional
from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import InstructionAddressBusValue
from simulator.modules.register_file import StatusRegisterValue
from simulator.modules.decoder import BranchCondition


class ProgramCounterState(BaseModuleState):
    value = 0
    next_value: Optional[int] = None


class ProgramCounter(BaseModule):
    def __init__(self, name: str):
        self.state = ProgramCounterState()
        super().__init__(name, self.state)

    def increment(self):
        """Increment the program counter."""
        self.state.next_value = self.state.value + 1

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
        """Conditionally branch based on the status register and branch condition."""
        branch = False
        if branch_condition == BranchCondition.ZERO:
            branch = status_register.zero
        elif branch_condition == BranchCondition.NOT_ZERO:
            branch = not status_register.zero
        elif branch_condition == BranchCondition.POSITIVE:
            branch = status_register.positive
        elif branch_condition == BranchCondition.NEGATIVE:
            branch = not status_register.positive
        elif branch_condition == BranchCondition.CARRY_SET:
            branch = status_register.carry_set
        elif branch_condition == BranchCondition.CARRY_CLEARED:
            branch = not status_register.carry_set
        elif branch_condition == BranchCondition.OVERFLOW_SET:
            branch = status_register.signed_overflow_set
        elif branch_condition == BranchCondition.OVERFLOW_CLEARED:
            branch = not status_register.signed_overflow_set

        if branch:
            self.jump_relative(offset)
        else:
            self.increment()

    def get_current_instruction_address(self):
        """Get the current instruction address."""
        return self.state.value

    def update_state(self) -> None:
        if self.state.next_value is not None:
            self.state.value = self.state.next_value
            self.state.next_value = None
        else:
            raise ValueError(
                "No next value set for program counter. Cannot update state."
            )
