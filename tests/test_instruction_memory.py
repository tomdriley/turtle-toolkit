import pytest
from simulator.modules.instruction_memory import (
    InstructionMemory,
    InstructionMemoryState,
)
from simulator.common.data_types import InstructionAddressBusValue
from simulator.common.config import INSTRUCTION_WIDTH


def test_fetch_valid_address():
    memory = bytes([0xAA, 0xBB, 0xCC, 0xDD])  # Example memory content
    state = InstructionMemoryState(memory=memory)
    instruction_memory = InstructionMemory(name="TestInstructionMemory", state=state)

    address = InstructionAddressBusValue(0)  # Valid address
    instruction = instruction_memory.fetch(address)

    assert instruction.raw_bytes == memory[: INSTRUCTION_WIDTH // 8]


def test_fetch_out_of_bounds():
    memory = bytes([0xAA, 0xBB, 0xCC, 0xDD])  # Example memory content
    state = InstructionMemoryState(memory=memory)
    instruction_memory = InstructionMemory(name="TestInstructionMemory", state=state)

    address = InstructionAddressBusValue(len(memory))  # Out-of-bounds address

    with pytest.raises(
        ValueError, match="Segmentation fault: address .* is out of bounds"
    ):
        instruction_memory.fetch(address)


def test_instruction_length_mismatch():
    memory = bytes([0xAA])  # Memory smaller than required instruction width
    state = InstructionMemoryState(memory=memory)
    instruction_memory = InstructionMemory(name="TestInstructionMemory", state=state)

    address = InstructionAddressBusValue(0)

    with pytest.raises(ValueError, match="Instruction must be .* bytes long"):
        instruction_memory.fetch(address)
