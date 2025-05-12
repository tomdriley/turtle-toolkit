import unittest
from simulator.modules.instruction_memory import InstructionMemory, INSTRUCTION_WIDTH
from simulator.common.data_types import InstructionAddressBusValue
from simulator.assembler import Assembler


class TestInstructionMemory(unittest.TestCase):
    def setUp(self):
        self.instruction_memory = InstructionMemory("InstructionMemory")

    def test_initial_state(self):
        """Test the initial state of the instruction memory"""
        self.assertEqual(len(self.instruction_memory.state.memory), 0)
        self.assertIsNone(self.instruction_memory.state.pending_address)
        self.assertIsNone(self.instruction_memory.state.pending_data)
        self.assertIsNone(self.instruction_memory.state.remaining_cycles)

    def test_fetch_after_side_load(self):
        """Test fetching instructions after side loading a binary"""
        # Create a test binary with two instructions
        instruction1 = b"\x00" * (INSTRUCTION_WIDTH // 8)
        instruction2 = b"\xff" * (INSTRUCTION_WIDTH // 8)
        binary = instruction1 + instruction2

        # Side load the binary
        self.instruction_memory.side_load(binary)

        # Fetch first instruction
        self.instruction_memory.request_fetch(InstructionAddressBusValue(0))
        for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
            self.assertFalse(self.instruction_memory.fetch_ready())
            self.instruction_memory.update_state()
        self.assertTrue(self.instruction_memory.fetch_ready())
        result = self.instruction_memory.get_fetch_result()
        self.assertEqual(result.data, instruction1)

        # Fetch second instruction
        self.instruction_memory.request_fetch(
            InstructionAddressBusValue(INSTRUCTION_WIDTH // 8)
        )
        for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
            self.instruction_memory.update_state()
        self.assertTrue(self.instruction_memory.fetch_ready())
        result = self.instruction_memory.get_fetch_result()
        self.assertEqual(result.data, instruction2)

    def test_fetch_after_side_load_str(self):
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
        self.instruction_memory.side_load(binary)

        # Fetch first instruction
        self.instruction_memory.request_fetch(InstructionAddressBusValue(0))
        for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
            self.assertFalse(self.instruction_memory.fetch_ready())
            self.instruction_memory.update_state()
        self.assertTrue(self.instruction_memory.fetch_ready())
        result = self.instruction_memory.get_fetch_result()
        self.assertEqual(result.data, Assembler.assemble(instruction1))

        # Fetch second instruction
        self.instruction_memory.request_fetch(
            InstructionAddressBusValue(INSTRUCTION_WIDTH // 8)
        )
        for _ in range(10):  # INSTRUCTION_FETCH_LATENCY_CYCLES
            self.instruction_memory.update_state()
        self.assertTrue(self.instruction_memory.fetch_ready())
        result = self.instruction_memory.get_fetch_result()
        self.assertEqual(result.data, Assembler.assemble(instruction2))

    def test_fetch_from_unloaded_address(self):
        """Test fetching from an address that hasn't been loaded"""
        self.instruction_memory.request_fetch(InstructionAddressBusValue(0))
        for _ in range(10):
            self.instruction_memory.update_state()
        self.assertTrue(self.instruction_memory.fetch_ready())
        with self.assertRaises(ValueError) as context:
            self.instruction_memory.get_fetch_result()
        self.assertIn("Segmentation fault", str(context.exception))

    def test_concurrent_fetches(self):
        """Test that concurrent fetches to different addresses fail"""
        self.instruction_memory.request_fetch(InstructionAddressBusValue(0))
        with self.assertRaises(ValueError) as context:
            self.instruction_memory.request_fetch(
                InstructionAddressBusValue(INSTRUCTION_WIDTH // 8)
            )
        self.assertIn("while another operation is pending", str(context.exception))

    def test_invalid_instruction_size(self):
        """Test that side loading instructions of wrong size fails"""
        invalid_binary = b"\x00" * (INSTRUCTION_WIDTH // 8 - 1)  # One byte too short
        self.instruction_memory.side_load(invalid_binary)
        self.assertEqual(
            len(self.instruction_memory.state.memory), 0
        )  # Should not store incomplete instruction

    def test_fetch_without_pending_request(self):
        """Test that getting fetch result without a pending request fails"""
        with self.assertRaises(ValueError) as context:
            self.instruction_memory.get_fetch_result()
        self.assertEqual("No read operation pending.", str(context.exception))
