"""data_memory.py - Data Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import DataAddressBusValue, DataBusValue

MEMORY_STORE_LATENCY_CYCLES = 10
MEMORY_LOAD_LATENCY_CYCLES = 10


@dataclass
class DataMemoryState(BaseModuleState):
    pending_address: Optional[DataAddressBusValue] = None
    pending_data: Optional[DataBusValue] = None
    load_remaining_cycles: Optional[int] = None
    store_remaining_cycles: Optional[int] = None
    memory: Dict[DataAddressBusValue, DataBusValue] = field(default_factory=dict)


class DataMemory(BaseModule):
    def __init__(self, name: str) -> None:
        self.state = DataMemoryState()
        super().__init__(name, self.state)

    def request_load(self, address: DataAddressBusValue):
        if (
            self.state.pending_address is not None
            and self.state.pending_address != address
        ):
            raise ValueError(
                f"Load request for address {address} while another load is pending for address {self.state.pending_address}."
            )
        self.state.pending_address = address
        if self.state.load_remaining_cycles is None:
            self.state.load_remaining_cycles = MEMORY_LOAD_LATENCY_CYCLES

    def load_ready(self) -> bool:
        ready = (
            self.state.load_remaining_cycles is not None
            and self.state.load_remaining_cycles == 0
        )
        if ready:
            self.state.load_remaining_cycles = None
        return ready

    def get_load_result(self) -> DataBusValue:
        if self.state.pending_address is None:
            raise ValueError("No load request pending.")
        load_result = self.state.memory.get(self.state.pending_address)
        if load_result is None:
            raise ValueError(
                f"Segmentation fault: address {self.state.pending_address} has not been written to yet."
            )
        # Only clear pending state after successfully getting the result
        self.state.pending_address = None
        self.state.pending_data = None
        return load_result

    def request_store(self, address: DataAddressBusValue, value: DataBusValue):
        if (
            self.state.pending_address is not None
            and self.state.pending_address != address
        ):
            raise ValueError(
                f"Store request for address {address} while another store is pending for address {self.state.pending_address}."
            )
        if self.state.pending_data is not None and self.state.pending_data != value:
            raise ValueError(
                f"Store request for value {value} while another store is pending for value {self.state.pending_data}."
            )
        self.state.pending_address = address
        self.state.pending_data = value
        if self.state.store_remaining_cycles is None:
            self.state.store_remaining_cycles = MEMORY_STORE_LATENCY_CYCLES

    def store_complete(self) -> bool:
        complete = (
            self.state.store_remaining_cycles is not None
            and self.state.store_remaining_cycles == 0
        )
        if complete:
            self.state.store_remaining_cycles = None
            if (
                self.state.pending_address is not None
                and self.state.pending_data is not None
            ):
                self.state.memory[self.state.pending_address] = self.state.pending_data
                self.state.pending_address = None
                self.state.pending_data = None
        return complete

    def update_state(self) -> None:
        if self.state.load_remaining_cycles is not None:
            self.state.load_remaining_cycles -= 1
        if self.state.store_remaining_cycles is not None:
            self.state.store_remaining_cycles -= 1
