"""simulator.py - Singleton class for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Generator, Optional
from dataclasses import dataclass

from simulator.common.singleton_meta import SingletonMeta
from simulator.common.logger import logger


@dataclass
class SimulatorState:
    """Class to hold the state of the simulator."""

    cycle_count: int = 0
    halted: bool = False
    # Add other state variables as needed

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

    def __init__(self):
        logger.debug("Initializing Simulator instance.")
        self._state = SimulatorState()
        logger.info("Simulator instance created.")

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
