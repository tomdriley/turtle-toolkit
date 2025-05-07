import unittest
from simulator.modules.data_memory import DataMemory
from simulator.common.data_types import DataBusValue, DataAddressBusValue


class TestDataMemory(unittest.TestCase):
    def setUp(self):
        self.data_memory = DataMemory("DataMemory")

    def test_initial_state(self):
        """Test the initial state of the data memory"""
        self.assertEqual(len(self.data_memory.state.memory), 0)
        self.assertIsNone(self.data_memory.state.pending_address)
        self.assertIsNone(self.data_memory.state.pending_data)
        self.assertIsNone(self.data_memory.state.load_remaining_cycles)
        self.assertIsNone(self.data_memory.state.store_remaining_cycles)

    def test_store_and_load(self):
        """Test basic store and load operations"""
        address = DataAddressBusValue(0x100)
        value = DataBusValue(42)

        # Store operation
        self.data_memory.request_store(address, value)
        for _ in range(10):  # MEMORY_STORE_LATENCY_CYCLES
            self.assertFalse(self.data_memory.store_complete())
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.store_complete())

        # Load operation
        self.data_memory.request_load(address)
        for _ in range(10):  # MEMORY_LOAD_LATENCY_CYCLES
            self.assertFalse(self.data_memory.load_ready())
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.load_ready())
        self.assertEqual(self.data_memory.get_load_result(), value)

    def test_load_from_unwritten_address(self):
        """Test loading from an address that hasn't been written to"""
        address = DataAddressBusValue(0x200)
        self.data_memory.request_load(address)
        for _ in range(10):
            self.data_memory.update_state()
        self.assertTrue(self.data_memory.load_ready())
        with self.assertRaises(ValueError) as context:
            self.data_memory.get_load_result()
        self.assertIn("Segmentation fault", str(context.exception))

    def test_concurrent_load_store_different_addresses(self):
        """Test that concurrent load/store operations to different addresses fail"""
        self.data_memory.request_store(DataAddressBusValue(0x100), DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_store(DataAddressBusValue(0x200), DataBusValue(43))
        self.assertIn("while another store is pending", str(context.exception))

    def test_load_during_store(self):
        """Test that loading while a store is in progress fails if different address"""
        self.data_memory.request_store(DataAddressBusValue(0x100), DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_load(DataAddressBusValue(0x200))
        self.assertIn("while another load is pending", str(context.exception))

    def test_store_same_address_different_value(self):
        """Test that storing different values to the same address fails"""
        address = DataAddressBusValue(0x100)
        self.data_memory.request_store(address, DataBusValue(42))
        with self.assertRaises(ValueError) as context:
            self.data_memory.request_store(address, DataBusValue(43))
        self.assertIn("while another store is pending", str(context.exception))

    def test_load_without_pending_request(self):
        """Test that getting load result without a pending request fails"""
        with self.assertRaises(ValueError) as context:
            self.data_memory.get_load_result()
        self.assertEqual("No load request pending.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
