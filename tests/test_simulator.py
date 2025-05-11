import unittest
from simulator.simulator import (
    Simulator,
    DATA_MEMORY_NAME,
    INSTRUCTION_MEMORY_NAME,
    PROGRAM_COUNTER_NAME,
)
from simulator.common.config import INSTRUCTION_WIDTH
from simulator.modules.instruction_memory import INSTRUCTION_FETCH_LATENCY_CYCLES
from simulator.assembler import Assembler


class TestSimulator(unittest.TestCase):
    def setUp(self):
        # Ensure the simulator is reset before each test
        self.simulator = Simulator()

    def test_initial_state(self):
        # Test the initial state of the simulator
        state = self.simulator.get_state()
        self.assertEqual(state.cycle_count, 0)
        self.assertFalse(state.halted)
        self.assertFalse(state.stalled)
        self.assertEqual(state.modules[DATA_MEMORY_NAME].memory, {})
        self.assertEqual(state.modules[INSTRUCTION_MEMORY_NAME].memory, {})
        self.assertEqual(state.modules[PROGRAM_COUNTER_NAME].value, 0)

    def test_tick(self):
        # Test the tick method increments the cycle count
        source = """
        NOP
        HALT
        """
        binary = Assembler.assemble(source)
        num_instructions = len(binary) // (INSTRUCTION_WIDTH // 8)
        self.simulator.load_binary(binary)
        initial_cycle_count = self.simulator.get_state().cycle_count
        final_cycle_count = initial_cycle_count + num_instructions * (
            1 + INSTRUCTION_FETCH_LATENCY_CYCLES
        )
        self.simulator.run_until_halt()
        self.assertEqual(self.simulator.get_state().cycle_count, final_cycle_count)

    def test_reset(self):
        # Test resetting the simulator
        self.simulator.reset()
        state = self.simulator.get_state()
        self.assertEqual(state.cycle_count, 0)
        self.assertFalse(state.halted)
        self.assertFalse(state.stalled)
        self.assertEqual(state.modules[DATA_MEMORY_NAME].memory, {})
        self.assertEqual(state.modules[INSTRUCTION_MEMORY_NAME].memory, {})
        self.assertEqual(state.modules[PROGRAM_COUNTER_NAME].value, 0)


if __name__ == "__main__":
    unittest.main()
