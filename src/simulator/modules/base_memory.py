"""base_memory.py - Base Memory module with common functionality
Author: Tom Riley
Date: 2025-05-06
"""

from typing import Dict, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from simulator.modules.base_module import BaseModule, BaseModuleState

AddressType = TypeVar("AddressType")
DataType = TypeVar("DataType")


@dataclass
class BaseMemoryState(BaseModuleState, Generic[AddressType, DataType]):
    """Common state for memory modules."""

    pending_address: Optional[AddressType] = None
    pending_data: Optional[DataType] = None
    remaining_cycles: Optional[int] = None
    memory: Dict[AddressType, DataType] = field(default_factory=dict)


class BaseMemory(BaseModule, Generic[AddressType, DataType]):
    """Base class for memory modules with common functionality."""

    def __init__(self, name: str, latency_cycles: int) -> None:
        self.state = BaseMemoryState[AddressType, DataType]()
        super().__init__(name, self.state)
        self._latency_cycles = latency_cycles

    def _start_operation(
        self, address: AddressType, data: Optional[DataType] = None
    ) -> None:
        """Start a memory operation with given address and optional data."""
        if (
            self.state.pending_address is not None
            and self.state.pending_address != address
        ):
            raise ValueError(
                f"Memory operation requested for address {address} while another operation "
                f"is pending for address {self.state.pending_address}."
            )
        if (
            data is not None
            and self.state.pending_data is not None
            and self.state.pending_data != data
        ):
            raise ValueError(
                f"Memory operation requested for value {data} while another operation "
                f"is pending for value {self.state.pending_data}."
            )
        self.state.pending_address = address
        self.state.pending_data = data
        if self.state.remaining_cycles is None:
            self.state.remaining_cycles = self._latency_cycles

    def operation_complete(self) -> bool:
        """Check if the current memory operation is complete."""
        complete = (
            self.state.remaining_cycles is not None and self.state.remaining_cycles == 0
        )
        if complete:
            self.state.remaining_cycles = None
        return complete

    def _complete_write(self) -> None:
        """Complete a write operation by updating memory with pending data."""
        if (
            self.state.pending_address is not None
            and self.state.pending_data is not None
        ):
            self.state.memory[self.state.pending_address] = self.state.pending_data
            self.state.pending_address = None
            self.state.pending_data = None

    def _read_value(self) -> DataType:
        """Read a value from memory at the pending address."""
        if self.state.pending_address is None:
            raise ValueError("No read operation pending.")
        value = self.state.memory.get(self.state.pending_address)
        if value is None:
            raise ValueError(
                f"Segmentation fault: address {self.state.pending_address} "
                "has not been written to yet."
            )
        # Only clear pending state after successfully getting the result
        self.state.pending_address = None
        self.state.pending_data = None
        return value

    def update_state(self) -> None:
        """Update the memory state for the current cycle."""
        if self.state.remaining_cycles is not None and self.state.remaining_cycles > 0:
            self.state.remaining_cycles -= 1
            assert (
                self.state.remaining_cycles is None or self.state.remaining_cycles >= 0
            )
