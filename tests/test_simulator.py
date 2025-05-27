import numpy as np
import pytest

from turtle_toolkit.assembler import Assembler
from turtle_toolkit.common.config import INSTRUCTION_WIDTH
from turtle_toolkit.common.data_types import DataAddressBusValue, DataBusValue
from turtle_toolkit.common.instruction_data import RegisterIndex
from turtle_toolkit.modules.instruction_memory import INSTRUCTION_FETCH_LATENCY_CYCLES
from turtle_toolkit.simulator import (
    DATA_MEMORY_NAME,
    INSTRUCTION_MEMORY_NAME,
    PROGRAM_COUNTER_NAME,
    REGISTER_FILE_NAME,
    SimulationTimeout,
    Simulator,
)


@pytest.fixture
def simulator() -> Simulator:
    """Provides a fresh simulator instance for each test."""
    sim = Simulator()
    sim.reset()
    return sim


def test_initial_state(simulator: Simulator) -> None:
    # Test the initial state of the simulator
    state = simulator.get_state()
    assert state.cycle_count == 0
    assert not state.halted
    assert not state.stalled
    assert state.modules[DATA_MEMORY_NAME].memory == {}
    assert state.modules[INSTRUCTION_MEMORY_NAME].memory == {}
    assert state.modules[PROGRAM_COUNTER_NAME].value == 0


def test_tick(simulator: Simulator) -> None:
    # Test the tick method increments the cycle count
    source = """
    NOP
    HALT
    """
    binary = Assembler.assemble(source)
    num_instructions = len(binary) // (INSTRUCTION_WIDTH // 8)
    simulator.load_binary(binary)
    initial_cycle_count = simulator.get_state().cycle_count
    final_cycle_count = initial_cycle_count + num_instructions * (
        1 + INSTRUCTION_FETCH_LATENCY_CYCLES
    )
    simulator.run_until_halt()
    assert simulator.get_state().cycle_count == final_cycle_count


def test_reset(simulator: Simulator) -> None:
    # Test resetting the simulator
    simulator.reset()
    state = simulator.get_state()
    assert state.cycle_count == 0
    assert not state.halted
    assert not state.stalled
    assert state.modules[DATA_MEMORY_NAME].memory == {}
    assert state.modules[INSTRUCTION_MEMORY_NAME].memory == {}
    assert state.modules[PROGRAM_COUNTER_NAME].value == 0


def test_set(simulator: Simulator) -> None:
    # Test the set instruction
    source = """
    SET 1
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_load_program(simulator: Simulator) -> None:
    # Test loading a program without assembling first
    source = """
    SET 1
    HALT
    """
    simulator.load_program(source)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_addi_instruction(simulator: Simulator) -> None:
    # Test the ADD instruction
    source = """
    SET 1
    ADDI 2
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(3))


def test_put_instruction(simulator: Simulator) -> None:
    # Test the PUT instruction
    source = """
    SET 1
    PUT R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.R0.value
    ] == DataBusValue(np.uint16(1))


def test_get_instruction(simulator: Simulator) -> None:
    # Test the GET instruction
    source = """
    SET 1
    PUT R0
    SET 0
    GET R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_add_instruction(simulator: Simulator) -> None:
    # Test the ADD instruction
    source = """
    SET 1
    PUT R0
    SET 2
    ADD R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(3))


def test_sub_instruction(simulator: Simulator) -> None:
    # Test the SUB instruction
    source = """
    SET 3
    PUT R0
    SET 5
    SUB R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(2))


def test_and_instruction(simulator: Simulator) -> None:
    # Test the AND instruction
    source = """
    SET 6  ; 0b0110
    PUT R0
    SET 5  ; 0b0101
    AND R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(
        4
    )  # 0b0100


def test_or_instruction(simulator: Simulator) -> None:
    # Test the OR instruction
    source = """
    SET 2  ; 0b0010
    PUT R0
    SET 4  ; 0b0100
    OR R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(
        6
    )  # 0b0110


def test_xor_instruction(simulator: Simulator) -> None:
    # Test the XOR instruction
    source = """
    SET 6  ; 0b0110
    PUT R0
    SET 3  ; 0b0011
    XOR R0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(
        5
    )  # 0b0101


def test_inv_instruction(simulator: Simulator) -> None:
    # Test the INV instruction
    source = """
    SET 0b00001111
    INV
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert DataBusValue(
        state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC.value]
    ).unsigned_value() == np.int16(0b11110000)


def test_subi_instruction(simulator: Simulator) -> None:
    # Test the SUBI instruction
    source = """
    SET 5
    SUBI 2
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(3))


def test_andi_instruction(simulator: Simulator) -> None:
    # Test the ANDI instruction
    source = """
    SET 0b0110
    ANDI 0b0101
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.int16(0b0100))


def test_ori_instruction(simulator: Simulator) -> None:
    # Test the ORI instruction
    source = """
    SET 0b0010
    ORI 0b0100
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.int16(0b0110))


def test_xori_instruction(simulator: Simulator) -> None:
    # Test the XORI instruction
    source = """
    SET 0b0110
    XORI 0b0011
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.int16(0b0101))


def test_jmpi_instruction(simulator: Simulator) -> None:
    # Test the JMPI instruction
    source = """
    SET 0
    JMPI 4
    SET 1
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_bz_instruction_taken(simulator: Simulator) -> None:
    # Test the BZ instruction
    source = """
    SET 0
    BZ 4
    SET 1
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_bz_instruction_not_taken(simulator: Simulator) -> None:
    # Test the BZ instruction
    source = """
    SET 1
    BZ 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_bnz_instruction_taken(simulator: Simulator) -> None:
    # Test the BNZ instruction
    source = """
    SET 1
    BNZ 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_bnz_instruction_not_taken(simulator: Simulator) -> None:
    # Test the BNZ instruction
    source = """
    SET 0
    BNZ 4
    SET 1
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_bp_instruction_taken(simulator: Simulator) -> None:
    # Test the BP instruction
    source = """
    SET 1
    BP 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_bp_instruction_not_taken(simulator: Simulator) -> None:
    # Test the BP instruction
    source = """
    SET -1
    BP 4
    SET 1
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == np.uint16(1)


def test_bn_instruction_taken(simulator: Simulator) -> None:
    # Test the BN instruction
    source = """
    SET -1
    BN 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert np.int16(
        state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC.value]
    ) == np.int16(-1)


def test_bn_instruction_not_taken(simulator: Simulator) -> None:
    # Test the BN instruction
    source = """
    SET 1
    BN 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_bcs_instruction_taken(simulator: Simulator) -> None:
    # Test the Brabch if Carry Set (BCS) instruction
    source = """
    SET 0xFF
    ADDI 6
    BCS 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(5))


def test_bcs_instruction_not_taken(simulator: Simulator) -> None:
    # Test the Branch if Carry Set (BCS) instruction
    source = """
    SET 0xFE
    ADDI 1
    BCS 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_bcc_instruction_taken(simulator: Simulator) -> None:
    # Test the Branch if Carry Clear (BCC) instruction
    source = """
    SET 0xFE
    ADDI 1
    BCC 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert DataBusValue(
        state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC.value]
    ) == DataBusValue(np.uint16(0xFF))


def test_bcc_instruction_not_taken(simulator: Simulator) -> None:
    # Test the Branch if Carry Clear (BCC) instruction
    source = """
    SET 0xFF
    ADDI 6
    BCC 4
    SET 0
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(0))


def test_watchdog_timer(simulator: Simulator) -> None:
    # Test that the watchdog timer works by creating an infinite loop
    source = """
    ; An infinite loop that never halts
    SET 0
    JMPI 0  ; Jump back to the same instruction, creating an infinite loop
    HALT     ; This should never be reached
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)

    # Run with a small max_cycles value (watchdog timer)
    max_cycles = 10

    # The simulation should raise a SimulationTimeout exception
    with pytest.raises(SimulationTimeout) as excinfo:
        simulator.run_until_halt(max_cycles=max_cycles)

    # Verify that the exception contains the correct cycle count
    assert excinfo.value.cycle_count == max_cycles


def test_store_instruction(simulator: Simulator) -> None:
    # Test the STORE instruction
    source = """
    SET 1
    STORE
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt(max_cycles=100)
    state = simulator.get_state()
    assert state.modules[DATA_MEMORY_NAME].memory[
        DataAddressBusValue(np.int16(0x000))
    ] == DataBusValue(np.uint16(1))


def test_load_instruction(simulator: Simulator) -> None:
    # Test the LOAD instruction
    source = """
    SET 1
    STORE
    SET 0
    LOAD
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt(max_cycles=100)
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_store_different_address(simulator: Simulator) -> None:
    # Test the STORE instruction with a different address
    source = """
    SET 1
    PUT DOFF ; Addr <= 0x001
    SET 0xA
    STORE ; Store 0x0A @ Addr 0x001
    SET 0
    PUT DOFF ; Addr <= 0x000
    STORE ; Store 0x00 @ Addr 0x000
    SET 1
    PUT DOFF ; Addr <= 0x001
    LOAD ; Load from Addr 0x001
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt(max_cycles=1000)
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(0x0A)


def test_store_load_different_address(simulator: Simulator) -> None:
    # Test the STORE and LOAD instructions with different addresses
    source = """
    SET 1
    PUT DOFF ; Addr <= 0x001
    STORE ; Store 0x01 @ Addr 0x001
    SET 0
    PUT DOFF ; Addr <= 0x000
    STORE ; Store 0x00 @ Addr 0x000
    SET 1
    PUT DOFF ; Addr <= 0x001
    SET 0x0A
    LOAD ; Load from Addr 0x001
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt(max_cycles=1000)
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.ACC.value
    ] == DataBusValue(np.uint16(1))


def test_all_registers(simulator: Simulator) -> None:
    # Test the initial state of all registers
    source = """
    SET 1
    PUT R0
    SET 2
    PUT R1
    SET 3
    PUT R2
    SET 4
    PUT R3
    SET 5
    PUT R4
    SET 6
    PUT R5
    SET 7
    PUT R6
    SET 8
    PUT R7
    HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt()

    state = simulator.get_state()

    for i in range(8):
        assert state.modules[REGISTER_FILE_NAME].registers[
            RegisterIndex(i).value
        ] == DataBusValue(np.uint16(i + 1))


def test_long_program(simulator: Simulator) -> None:
    # Test a long program that runs for many cycles
    source = """
        SET 0
        PUT R1
        PUT R2
        SET 200
        PUT R3
        SET 100
        PUT R0
        GET R0
        BZ 26
        GET R1
        ADD R3
        PUT R1
        BCS 4
        JMPI 8
        GET R2
        ADDI 1
        PUT R2
        GET R0
        SUBI 1
        PUT R0
        JMPI -26
        HALT
    """
    binary = Assembler.assemble(source)
    simulator.load_binary(binary)
    simulator.run_until_halt(max_cycles=100000000)
    state = simulator.get_state()
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.R2.value
    ] == DataBusValue(np.int16(0x4E))
    assert state.modules[REGISTER_FILE_NAME].registers[
        RegisterIndex.R1.value
    ] == DataBusValue(np.int16(0x20))
    cycle_count = simulator.get_state().cycle_count
    print(f"Cycle count: {cycle_count}")  # This will be captured by capsys
