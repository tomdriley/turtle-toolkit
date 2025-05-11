"""instruction_memory.py - Instruction Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from simulator.common.data_types import InstructionAddressBusValue
from simulator.common.config import INSTRUCTION_WIDTH
from simulator.modules.base_memory import BaseMemory

INSTRUCTION_FETCH_LATENCY_CYCLES = 10


@dataclass
class Instruction:
    data: bytes | str

    def __repr__(self):
        if isinstance(self.data, bytes):
            return f"Instruction({self.data.hex()})"
        return f"Instruction({self.data})"

    def __post_init__(self):
        if isinstance(self.data, bytes) and len(self.data) != INSTRUCTION_WIDTH // 8:
            raise ValueError(
                f"Instruction must be {INSTRUCTION_WIDTH // 8} bytes long, "
                + f"but got {len(self.raw_bytes)} bytes."
            )


class InstructionMemory(BaseMemory[InstructionAddressBusValue, Instruction]):
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
                self.state.memory[InstructionAddressBusValue(addr)] = Instruction(chunk)

    def request_fetch(self, address: InstructionAddressBusValue) -> None:
        """Request a fetch operation from instruction memory."""
        self._start_operation(address)

    def fetch_ready(self) -> bool:
        """Check if the fetch operation is complete."""
        return self.operation_complete()

    def get_fetch_result(self) -> Instruction:
        """Get the result of the fetch operation."""
        return self._read_value()
