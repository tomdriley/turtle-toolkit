"""data_memory.py - Data Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_memory import BaseMemory
from simulator.common.data_types import DataAddressBusValue, DataBusValue

MEMORY_LATENCY_CYCLES = 10


class DataMemory(BaseMemory[DataAddressBusValue, DataBusValue]):
    def __init__(self, name: str) -> None:
        super().__init__(name, MEMORY_LATENCY_CYCLES)

    def request_load(self, address: DataAddressBusValue) -> None:
        """Request a load operation from data memory."""
        self._start_operation(address)

    def load_ready(self) -> bool:
        """Check if the load operation is complete."""
        return self.operation_complete()

    def get_load_result(self) -> DataBusValue:
        """Get the result of the load operation."""
        return self._read_value()

    def request_store(self, address: DataAddressBusValue, value: DataBusValue) -> None:
        """Request a store operation to data memory."""
        self._start_operation(address, value)

    def store_complete(self) -> bool:
        """Check if the store operation is complete."""
        complete = self.operation_complete()
        if complete:
            self._complete_write()
        return complete
