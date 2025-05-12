import unittest
from simulator.modules.data_memory import DataMemory
from simulator.common.data_types import DataAddressBusValue, DataBusValue


class TestDataMemory(unittest.TestCase):
    def setUp(self):
        self.data_memory = DataMemory("DataMemory")

    def test_initial_state(self):
        """Test the initial state of the data memory"""
        self.assertEqual(len(self.data_memory.state.memory), 0)
        self.assertIsNone(self.data_memory.state.pending_address)
        self.assertIsNone(self.data_memory.state.pending_data)
        self.assertIsNone(self.data_memory.state.remaining_cycles)

    def test_store_and_load(self):
        """Test storing and then loading a value"""
        address = DataAddressBusValue(0x100)
        value = DataBusValue(42)

        # Store the value
        self.data_memory.request_store(address, value)
        for _ in range(10):  # MEMORY_LATENCY_CYCLES
            self.assertFalse(self.data_memory.store_complete())
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.store_complete())

        # Load the value back
        self.data_memory.request_load(address)
        for _ in range(10):  # MEMORY_LATENCY_CYCLES
            self.assertFalse(self.data_memory.load_ready())
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.load_ready())
        result = self.data_memory.get_load_result()
        self.assertEqual(result, value)

    def test_concurrent_load_store_different_addresses(self):
        """Test that concurrent load/store operations to different addresses fail"""
        self.data_memory.request_store(DataAddressBusValue(0x100), DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_store(DataAddressBusValue(0x200), DataBusValue(43))
        self.assertIn("while another operation is pending", str(context.exception))

    def test_load_during_store(self):
        """Test that loading while a store is in progress fails if different address"""
        self.data_memory.request_store(DataAddressBusValue(0x100), DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_load(DataAddressBusValue(0x200))
        self.assertIn("while another operation is pending", str(context.exception))

    def test_store_same_address_different_value(self):
        """Test that storing different values to the same address fails"""
        address = DataAddressBusValue(0x100)
        self.data_memory.request_store(address, DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_store(address, DataBusValue(43))
        self.assertIn("while another operation is pending", str(context.exception))

    def test_load_without_pending_request(self):
        """Test that getting load result without a pending request fails"""
        with self.assertRaises(ValueError) as context:
            self.data_memory.get_load_result()
        self.assertEqual("No read operation pending.", str(context.exception))

    def test_load_from_unwritten_address(self):
        """Test that loading from an unwritten address fails"""
        self.data_memory.request_load(DataAddressBusValue(0x100))
        for _ in range(10):  # MEMORY_LATENCY_CYCLES
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.load_ready())
        with self.assertRaises(ValueError) as context:
            self.data_memory.get_load_result()
        self.assertIn("Segmentation fault", str(context.exception))
