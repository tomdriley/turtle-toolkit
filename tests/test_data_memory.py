import numpy as np
import pytest

from turtle_toolkit.common.data_types import DataAddressBusValue, DataBusValue
from turtle_toolkit.modules.data_memory import DataMemory


@pytest.fixture
def data_memory():
    return DataMemory("DataMemory")


def test_initial_state(data_memory):
    """Test the initial state of the data memory"""
    assert len(data_memory.state.memory) == 0
    assert data_memory.state.pending_address is None
    assert data_memory.state.pending_data is None
    assert data_memory.state.remaining_cycles is None


def test_store_and_load(data_memory):
    """Test storing and then loading a value"""
    address = DataAddressBusValue(np.int16(0x100))
    value = DataBusValue(np.uint16(42))

    # Store the value
    data_memory.request_store(address, value)
    for _ in range(10):  # MEMORY_LATENCY_CYCLES
        assert not data_memory.store_complete()
        data_memory.update_state()
    assert data_memory.store_complete()

    # Load the value back
    data_memory.request_load(address)
    for _ in range(10):  # MEMORY_LATENCY_CYCLES
        assert not data_memory.load_ready()
        data_memory.update_state()
    assert data_memory.load_ready()
    result = data_memory.get_load_result()
    assert result == value


def test_concurrent_load_store_different_addresses(data_memory):
    """Test that concurrent load/store operations to different addresses fail"""
    data_memory.request_store(
        DataAddressBusValue(np.int16(0x100)), DataBusValue(np.uint16(42))
    )
    with pytest.raises(ValueError) as excinfo:
        data_memory.request_store(
            DataAddressBusValue(np.int16(0x200)), DataBusValue(np.uint16(43))
        )
    assert "while another operation is pending" in str(excinfo.value)


def test_load_during_store(data_memory):
    """Test that loading while a store is in progress fails if different address"""
    data_memory.request_store(
        DataAddressBusValue(np.int16(0x100)), DataBusValue(np.uint16(42))
    )
    with pytest.raises(ValueError) as excinfo:
        data_memory.request_load(DataAddressBusValue(np.int16(0x200)))
    assert "while another operation is pending" in str(excinfo.value)


def test_store_same_address_different_value(data_memory):
    """Test that storing different values to the same address fails"""
    address = DataAddressBusValue(np.int16(0x100))
    data_memory.request_store(address, DataBusValue(np.uint16(42)))
    with pytest.raises(ValueError) as excinfo:
        data_memory.request_store(address, DataBusValue(np.uint16(43)))
    assert "while another operation is pending" in str(excinfo.value)


def test_load_without_pending_request(data_memory):
    """Test that getting load result without a pending request fails"""
    with pytest.raises(ValueError) as excinfo:
        data_memory.get_load_result()
    assert "No read operation pending." == str(excinfo.value)


def test_load_from_unwritten_address(data_memory):
    """Test that loading from an unwritten address fails"""
    data_memory.request_load(DataAddressBusValue(np.int16(0x100)))
    for _ in range(10):  # MEMORY_LATENCY_CYCLES
        data_memory.update_state()
    assert data_memory.load_ready()
    with pytest.raises(ValueError) as excinfo:
        data_memory.get_load_result()
    assert "Segmentation fault" in str(excinfo.value)
