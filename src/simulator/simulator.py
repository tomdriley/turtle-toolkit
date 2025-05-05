"""simulator.py - Singleton class for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Generator, Optional, Dict
from dataclasses import dataclass, field

from simulator.common.singleton_meta import SingletonMeta
from simulator.common.logger import logger
from simulator.modules.base_module import BaseModule, BaseModuleState
from simulator.modules.alu import ALU
from simulator.modules.decoder import DecodeUnit
from simulator.modules.instruction_memory import (
    InstructionMemory,
    InstructionMemoryState,
)
from simulator.modules.data_memory import DataMemory, DataMemoryState
from simulator.modules.register_file import RegisterFile, RegisterFileState
from simulator.modules.program_counter import ProgramCounter, ProgramCounterState


@dataclass
class SimulatorState:
    """Class to hold the state of the simulator."""

    cycle_count: int = 0
    halted: bool = False
    modules: Dict[str, BaseModuleState] = field(default_factory=dict)

    def tick(self) -> None:
        """Increment the cycle count"""
        self.cycle_count += 1
        logger.debug(f"Simulator tick: cycle count is now {self.cycle_count}.")


@dataclass
class SimulationResult:
    """Class to hold the result of the simulation."""

    cycle_count: int
    state: SimulatorState
    # Add other result variables as needed


class Simulator(metaclass=SingletonMeta):
    """Singleton class for the simulator."""

    _state: SimulatorState
    _modules: Dict[str, BaseModule] = {}

    def __init__(self):
        logger.debug("Initializing Simulator instance.")
        self._state = SimulatorState()
        self.create_and_initialize_modules()
        logger.info("Simulator instance created.")

    def create_and_initialize_modules(self, binary: bytes = b""):
        name = "ALU"
        self._modules[name] = ALU(name)
        name = "DecodeUnit"
        self._modules[name] = DecodeUnit(name)
        name = "InstructionMemory"
        # Sideload the binary data into the instruction memory
        instruction_memory_state = InstructionMemoryState(binary)
        self._state.modules[name] = instruction_memory_state
        self._modules[name] = InstructionMemory(name, instruction_memory_state)
        name = "DataMemory"
        data_memory_state = DataMemoryState()
        self._state.modules[name] = data_memory_state
        self._modules[name] = DataMemory(name, data_memory_state)
        name = "RegisterFile"
        register_file_state = RegisterFileState()
        self._state.modules[name] = register_file_state
        self._modules[name] = RegisterFile(name, register_file_state)
        name = "ProgramCounter"
        program_counter_state = ProgramCounterState()
        self._state.modules[name] = program_counter_state
        self._modules[name] = ProgramCounter(name, program_counter_state)

    def _execute_cycle(self) -> SimulatorState:
        """Execute a single cycle of the simulation."""
        logger.debug(f"Executing cycle {self._state.cycle_count}.")
        self._state.tick()
        # Placeholder for actual cycle execution logic
        # Update the state as needed
        return self._state

    def run(
        self, num_cycles: Optional[int]
    ) -> Generator[SimulatorState, None, SimulationResult]:
        logger.debug(f"Running simulator for {num_cycles} cycles.")
        cycles_run = 0
        while True:
            if num_cycles is not None and cycles_run >= num_cycles:
                logger.info("Reached the specified number of cycles.")
                break
            self._execute_cycle()
            if self._state.halted:
                logger.info(f"Simulation halted at cycle {self._state.cycle_count}.")
                break
            yield self._state
            cycles_run += 1
        logger.info(f"Simulation completed after {self._state.cycle_count} cycles.")
        return SimulationResult(self._state.cycle_count, self._state)

    def reset(self) -> None:
        """Reset the simulator state."""
        logger.debug("Resetting simulator state.")
        self._state = SimulatorState()
        logger.info("Simulator state reset.")
