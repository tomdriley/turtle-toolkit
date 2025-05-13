import pytest

from turtle_toolkit.assembler import Assembler
from turtle_toolkit.common.data_types import InstructionAddressBusValue
from turtle_toolkit.modules.instruction_memory import (
    INSTRUCTION_WIDTH,
    InstructionMemory,
)


@pytest.fixture
def instruction_memory():
    return InstructionMemory("InstructionMemory")


def test_initial_state(instruction_memory):
    """Test the initial state of the instruction memory"""
    assert len(instruction_memory.state.memory) == 0
    assert instruction_memory.state.pending_address is None
    assert instruction_memory.state.pending_data is None
    assert instruction_memory.state.remaining_cycles is None


def test_fetch_after_side_load(instruction_memory):
    """Test fetching instructions after side loading a binary"""
    # Create a test binary with two instructions
    instruction1 = b"\x00" * (INSTRUCTION_WIDTH // 8)
    instruction2 = b"\xff" * (INSTRUCTION_WIDTH // 8)
    binary = instruction1 + instruction2

    # Side load the binary
    instruction_memory.side_load(binary)

    # Fetch first instruction
    instruction_memory.request_fetch(InstructionAddressBusValue(0))
    for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
        assert not instruction_memory.fetch_ready()
        instruction_memory.update_state()
    assert instruction_memory.fetch_ready()
    result = instruction_memory.get_fetch_result()
    assert result.data == instruction1

    # Fetch second instruction
    instruction_memory.request_fetch(InstructionAddressBusValue(INSTRUCTION_WIDTH // 8))
    for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
        instruction_memory.update_state()
    assert instruction_memory.fetch_ready()
    result = instruction_memory.get_fetch_result()
    assert result.data == instruction2


def test_fetch_after_side_load_str(instruction_memory):
    """Test fetching instructions after side loading a binary"""
    # Create a test binary with two instructions
    instruction1 = "SET 10"
    comment_ignored = "      ; This is a comment"
    instruction2 = "ADD R1"
    second_comment = " ; Another comment"
    program = (
        instruction1
        + comment_ignored
        + "\n"
        + instruction2
        + "\n\n\n\n"
        + second_comment
    )

    binary = Assembler.assemble(program)

    # Side load the binary
    instruction_memory.side_load(binary)

    # Fetch first instruction
    instruction_memory.request_fetch(InstructionAddressBusValue(0))
    for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
        assert not instruction_memory.fetch_ready()
        instruction_memory.update_state()
    assert instruction_memory.fetch_ready()
    result = instruction_memory.get_fetch_result()
    assert result.data == Assembler.assemble(instruction1)

    # Fetch second instruction
    instruction_memory.request_fetch(InstructionAddressBusValue(INSTRUCTION_WIDTH // 8))
    for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
        instruction_memory.update_state()
    assert instruction_memory.fetch_ready()
    result = instruction_memory.get_fetch_result()
    assert result.data == Assembler.assemble(instruction2)


def test_fetch_from_unloaded_address(instruction_memory):
    """Test fetching from an address that hasn't been loaded"""
    instruction_memory.request_fetch(InstructionAddressBusValue(0))
    for _ in range(10):
        instruction_memory.update_state()
    assert instruction_memory.fetch_ready()
    with pytest.raises(ValueError) as excinfo:
        instruction_memory.get_fetch_result()
    assert "Segmentation fault" in str(excinfo.value)


def test_concurrent_fetches(instruction_memory):
    """Test that concurrent fetches to different addresses fail"""
    instruction_memory.request_fetch(InstructionAddressBusValue(0))
    with pytest.raises(ValueError) as excinfo:
        instruction_memory.request_fetch(
            InstructionAddressBusValue(INSTRUCTION_WIDTH // 8)
        )
    assert "while another operation is pending" in str(excinfo.value)


def test_invalid_instruction_size(instruction_memory):
    """Test that side loading instructions of wrong size fails"""
    invalid_binary = b"\x00" * (INSTRUCTION_WIDTH // 8 - 1)  # One byte too short
    instruction_memory.side_load(invalid_binary)
    assert (
        len(instruction_memory.state.memory) == 0
    )  # Should not store incomplete instruction


def test_fetch_without_pending_request(instruction_memory):
    """Test that getting fetch result without a pending request fails"""
    with pytest.raises(ValueError) as excinfo:
        instruction_memory.get_fetch_result()
    assert "No read operation pending." == str(excinfo.value)
