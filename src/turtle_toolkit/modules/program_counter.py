"""program_counter.py - Program Counter module
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Optional

from turtle_toolkit.common.config import INSTRUCTION_WIDTH
from turtle_toolkit.common.data_types import InstructionAddressBusValue
from turtle_toolkit.modules.base_module import BaseModule, BaseModuleState
from turtle_toolkit.modules.decoder import BranchCondition
from turtle_toolkit.modules.register_file import StatusRegisterValue


class ProgramCounterState(BaseModuleState):
    value = InstructionAddressBusValue(0)
    next_value: Optional[InstructionAddressBusValue] = None
    stall: bool = False


class ProgramCounter(BaseModule):
    def __init__(self, name: str):
        self.state = ProgramCounterState()
        super().__init__(name, self.state)

    def increment(self):
        """Increment the program counter."""
        self.state.next_value = self.state.value + InstructionAddressBusValue(
            INSTRUCTION_WIDTH // 8
        )

    def jump_relative(self, offset: InstructionAddressBusValue):
        """Set the program counter to a specific value."""
        self.state.next_value = self.state.value + offset

    def jump_absolute(self, address: InstructionAddressBusValue):
        """Set the program counter to a specific value."""
        self.state.next_value = address

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

    def set_stall(self, stall: bool) -> None:
        """Set the stall state of the program counter."""
        self.state.stall = stall

    def update_state(self) -> None:
        if self.state.stall:
            # If the program counter is stalled, do not update the value.
            return
        if self.state.next_value is not None:
            self.state.value = self.state.next_value
            self.state.next_value = None
        else:
            raise ValueError(
                "No next value set for program counter. Cannot update state."
            )
