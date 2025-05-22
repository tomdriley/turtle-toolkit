"""instruction_memory.py - Instruction Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass

import numpy as np

from turtle_toolkit.common.config import INSTRUCTION_WIDTH
from turtle_toolkit.common.data_types import InstructionAddressBusValue
from turtle_toolkit.modules.base_memory import BaseMemory

INSTRUCTION_FETCH_LATENCY_CYCLES = 10


@dataclass
class InstructionBinary:
    data: bytes

    def __repr__(self) -> str:
        return f"Instruction({self.data.hex()})"

    def __post_init__(self) -> None:
        if isinstance(self.data, bytes) and len(self.data) != INSTRUCTION_WIDTH // 8:
            raise ValueError(
                f"Instruction must be {INSTRUCTION_WIDTH // 8} bytes long, "
                + f"but got {len(self.data)} bytes."
            )
        elif isinstance(self.data, int) and (0 <= self.data < 2**INSTRUCTION_WIDTH):
            self.data = self.data.to_bytes(INSTRUCTION_WIDTH // 8, byteorder="little")


class InstructionMemory(BaseMemory[InstructionAddressBusValue, InstructionBinary]):
    def __init__(self, name: str) -> None:
        super().__init__(name, INSTRUCTION_FETCH_LATENCY_CYCLES)

    def side_load(self, binary: bytes) -> None:
        """Load binary data into memory."""
        # Clear any existing memory
        self.state.memory.clear()

        # Split binary into instruction-sized chunks and load into memory
        chunk_size = INSTRUCTION_WIDTH // 8
        for addr in range(0, len(binary), chunk_size):
            chunk = binary[addr : addr + chunk_size]
            if len(chunk) == chunk_size:  # Only store complete instructions
                self.state.memory[InstructionAddressBusValue(np.uint16(addr))] = (
                    InstructionBinary(chunk)
                )

    def request_fetch(self, address: InstructionAddressBusValue) -> None:
        """Request a fetch operation from instruction memory."""
        self._start_operation(address)

    def fetch_ready(self) -> bool:
        """Check if the fetch operation is complete."""
        return self.operation_complete()

    def get_fetch_result(self) -> InstructionBinary:
        """Get the result of the fetch operation."""
        return self._read_value()
