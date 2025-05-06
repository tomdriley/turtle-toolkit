"""data_memory.py - Data Memory module
Author: Tom Riley
Date: 2025-05-04
"""

from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.common.data_types import DataAddressBusValue, DataBusValue


class DataMemoryState(BaseModuleState):
    pass


class DataMemory(BaseModule):
    def __init__(self, name: str) -> None:
        self.state = DataMemoryState()
        super().__init__(name, self.state)

    def request_load(self, address: DataAddressBusValue):
        raise NotImplementedError()

    def load_ready(self) -> bool:
        raise NotImplementedError()

    def get_load_result(self) -> DataBusValue:
        raise NotImplementedError()

    def request_store(self, address: DataAddressBusValue, value: DataBusValue):
        raise NotImplementedError()

    def store_complete(self) -> bool:
        raise NotImplementedError()

    def update_state(self) -> None:
        raise NotImplementedError()
