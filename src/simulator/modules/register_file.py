"""register_file.py - Register File module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule, BaseModuleState


class RegisterFileState(BaseModuleState):
    def __init__(self):
        super().__init__()
        self.registers = [0] * 32  # Initialize 32 registers


class RegisterFile(BaseModule):
    def __init__(self, name: str, state: RegisterFileState):
        super().__init__(name)
        self.state = state

    def read(self, register_index):
        """Read value from a register."""
        return self.state.registers[register_index]

    def write(self, register_index, value):
        """Write value to a register."""
        self.state.registers[register_index] = value
