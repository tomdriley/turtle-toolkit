"""instruction_memory.py - Instruction Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from simulator.common.data_types import InstructionAddressBusValue
from simulator.common.config import INSTRUCTION_WIDTH
from simulator.modules.base_module import BaseModule, BaseModuleState


@dataclass
class Instruction:
    raw_bytes: bytes

    def __post_init__(self):
        if len(self.raw_bytes) != INSTRUCTION_WIDTH // 8:
            raise ValueError(
                f"Instruction must be {INSTRUCTION_WIDTH // 8} bytes long, "
                + f"but got {len(self.raw_bytes)} bytes."
            )


@dataclass
class InstructionMemoryState(BaseModuleState):
    memory: bytes


class InstructionMemory(BaseModule):
    def __init__(self, name: str, state: InstructionMemoryState) -> None:
        super().__init__(name, state)
        self._state = state  # redundant, but for clarity of the type

    def fetch(self, address: InstructionAddressBusValue) -> Instruction:
        """Fetch instruction from memory."""
        if address.unsigned_value() >= len(self._state.memory):
            raise ValueError(
                f"Segmentation fault: address {address} is out of bounds. "
                + f"Memory size is {len(self._state.memory)} bytes."
            )
        instruction = Instruction(
            raw_bytes=self._state.memory[
                address.unsigned_value() : address.unsigned_value()
                + INSTRUCTION_WIDTH // 8
            ]
        )
        return instruction
