"""program_counter.py - Program Counter module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule, BaseModuleState


class ProgramCounterState(BaseModuleState):
    def __init__(self):
        super().__init__()
        self.value = 0  # Initialize program counter


class ProgramCounter(BaseModule):
    def __init__(self, name: str, state: ProgramCounterState):
        super().__init__(name)
        self.state = state

    def increment(self):
        """Increment the program counter."""
        self.state.value += 1

    def set(self, value):
        """Set the program counter to a specific value."""
        self.state.value = value

    def get(self):
        """Get the current value of the program counter."""
        return self.state.value
