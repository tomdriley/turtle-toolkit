"""simulator.py - Singleton class for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from typing import Generator, Optional, Dict
from dataclasses import dataclass, field

from simulator.common.singleton_meta import SingletonMeta
from simulator.common.logger import logger
from simulator.common.data_types import DataBusValue
from simulator.modules.base_module import BaseModuleState
from simulator.modules.alu import ALU
from simulator.modules.decoder import DecodeUnit
from simulator.modules.instruction_memory import (
    InstructionMemory,
)
from simulator.modules.data_memory import DataMemory
from simulator.modules.register_file import RegisterFile
from simulator.modules.program_counter import ProgramCounter


@dataclass
class SimulatorState:
    """Class to hold the state of the simulator."""

    cycle_count: int = 0
    halted: bool = False
    stalled: bool = False
    modules: Dict[str, BaseModuleState] = field(default_factory=dict)
    acc_next: Optional[DataBusValue] = None
    acc_value: Optional[DataBusValue] = None

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
    _alu: ALU = ALU("ALU")
    _decode_unit: DecodeUnit = DecodeUnit("DecodeUnit")
    _instruction_memory: InstructionMemory = InstructionMemory("InstructionMemory")
    _data_memory: DataMemory = DataMemory("DataMemory")
    _register_file: RegisterFile = RegisterFile("RegisterFile")
    _program_counter: ProgramCounter = ProgramCounter("ProgramCounter")

    def __init__(self):
        logger.debug("Initializing Simulator instance.")
        self._state = SimulatorState()
        self.initialize_modules()
        logger.info("Simulator instance created.")

    def initialize_modules(self, binary: bytes = b""):
        self._instruction_memory.side_load_binary(binary)
        self._state.modules[self._instruction_memory.name] = (
            self._instruction_memory.get_state_ref()
        )
        self._state.modules[self._data_memory.name] = self._data_memory.get_state_ref()
        self._state.modules[self._register_file.name] = (
            self._register_file.get_state_ref()
        )
        self._state.modules[self._program_counter.name] = (
            self._program_counter.get_state_ref()
        )

    def _execute_cycle(self) -> SimulatorState:
        """Execute a single cycle of the simulation."""
        logger.debug(f"Executing cycle {self._state.cycle_count}.")
        instruction_address = self._program_counter.get_current_instruction_address()
        logger.debug(f"Fetching instruction from address {instruction_address}.")
        self._instruction_memory.request_fetch(instruction_address)
        self._state.stalled = not self._instruction_memory.fetch_ready()
        if self._state.stalled:
            logger.debug("Instruction fetch not ready, skipping this cycle.")
            return self._state
        else:
            logger.debug("Instruction fetch ready, proceeding.")
        instruction = self._instruction_memory.get_fetch_result()
        logger.debug(f"Fetched instruction: {instruction.raw_bytes.hex()}.")
        decoded_instruction = self._decode_unit.decode(instruction)
        if decoded_instruction.nop_instruction:
            logger.debug("NOP instruction encountered, skipping this cycle.")
            return self._state
        if decoded_instruction.halt_instruction:
            logger.info("HALT instruction encountered, stopping simulation.")
            self._state.halted = True
            return self._state
        self._state.acc_value = self._register_file.get_acc_value()
        logger.debug(f"Accumulator value: {self._state.acc_value}.")
        if decoded_instruction.alu_immediate_instruction:
            operand_b_bus_value = decoded_instruction.immediate_data_value
            logger.debug(f"Using immediate value: {operand_b_bus_value}.")
        else:
            operand_b_bus_value = self._register_file.get_register_value(
                decoded_instruction.register_index
            )
            logger.debug(f"Using register value: {operand_b_bus_value}.")
        if self._state.acc_value is not None:
            alu_outputs = self._alu.execute(
                self._state.acc_value,
                operand_b_bus_value,
                decoded_instruction.alu_function,
            )
        else:
            logger.fatal("Accumulator value is None, cannot execute ALU instruction.")
            raise ValueError(
                "Accumulator value is None, cannot execute ALU instruction."
            )
        if decoded_instruction.alu_instruction:
            self._state.acc_next = alu_outputs.result
            logger.debug(f"ALU result: {self._state.acc_next}.")
        elif decoded_instruction.memory_instruction and decoded_instruction.memory_load:
            self._data_memory.request_load(self._register_file.get_dmar_value())
            self._state.stalled = not self._data_memory.load_ready()
            if self._state.stalled:
                logger.debug("Memory load not ready, skipping this cycle.")
                return self._state
            else:
                self._state.acc_next = self._data_memory.get_load_result()
                logger.debug(f"Memory load result: {self._state.acc_next}.")
        elif (
            decoded_instruction.register_file_instruction
            and decoded_instruction.register_file_set
        ):
            self._state.acc_next = decoded_instruction.immediate_data_value
        elif (
            decoded_instruction.register_file_instruction
            and decoded_instruction.register_file_get
        ):
            self._state.acc_next = self._register_file.get_register_value(
                decoded_instruction.register_index
            )
        else:
            self._state.acc_next = self._state.acc_value
        if (
            decoded_instruction.register_file_instruction
            and decoded_instruction.register_file_put
        ):
            self._register_file.set_next_register_value(
                decoded_instruction.register_index, self._state.acc_value
            )
            logger.debug(
                f"Register {decoded_instruction.register_index} set to {self._state.acc_value}."
            )
        if decoded_instruction.memory_instruction and decoded_instruction.memory_store:
            self._data_memory.request_store(
                self._register_file.get_dmar_value(), self._state.acc_value
            )
            self._state.stalled = not self._data_memory.store_complete()
            if self._state.stalled:
                logger.debug("Memory store not complete, skipping this cycle.")
                return self._state
            else:
                self._state.acc_next = self._data_memory.get_load_result()
                logger.debug(
                    f"Stored {self._state.acc_value} to memory address {self._register_file.get_dmar_value()}."
                )
        if decoded_instruction.branch_instruction:
            self._program_counter.conditionally_branch(
                self._register_file.get_status_register_value(),
                decoded_instruction.immediate_address_value,
                decoded_instruction.branch_condition,
            )
        if decoded_instruction.jump_instruction and decoded_instruction.immediate_jump:
            self._program_counter.jump_relative(
                decoded_instruction.immediate_address_value
            )
        elif (
            decoded_instruction.jump_instruction
            and decoded_instruction.register_jump
            and decoded_instruction.relative_jump
        ):
            self._program_counter.jump_relative(self._register_file.get_imar_value())
        elif (
            decoded_instruction.jump_instruction
            and decoded_instruction.register_jump
            and not decoded_instruction.relative_jump
        ):
            self._program_counter.jump_absolute(self._register_file.get_imar_value())
        else:
            self._program_counter.increment()
        self._register_file.set_next_acc_value(self._state.acc_next)
        return self._state

    def _update_module_states(self) -> None:
        self._register_file.update_state()
        self._instruction_memory.update_state()
        self._data_memory.update_state()
        self._program_counter.update_state()

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
            cycles_run += 1
            self._state.tick()
            if self._state.halted:
                logger.info(f"Simulation halted at cycle {self._state.cycle_count}.")
                break
            yield self._state
            self._update_module_states()
        logger.info(f"Simulation completed after {self._state.cycle_count} cycles.")
        return SimulationResult(self._state.cycle_count, self._state)

    def reset(self) -> None:
        """Reset the simulator state."""
        logger.debug("Resetting simulator state.")
        self._state = SimulatorState()
        logger.info("Simulator state reset.")
