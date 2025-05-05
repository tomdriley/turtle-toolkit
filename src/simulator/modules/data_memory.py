"""data_memory.py - Data Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule, BaseModuleState


class DataMemoryState(BaseModuleState):
    def __init__(self):
        super().__init__()
        self.memory = {}  # Initialize data memory


class DataMemory(BaseModule):
    def __init__(self, name: str, state: DataMemoryState):
        super().__init__(name)
        self.state = state

    def read(self, address):
        """Read data from memory."""
        return self.state.memory.get(address, 0)

    def write(self, address, value):
        """Write data to memory."""
        self.state.memory[address] = value
