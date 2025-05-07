import unittest
from simulator.simulator import Simulator


class TestSimulator(unittest.TestCase):
    def setUp(self):
        # Ensure the simulator is reset before each test
        self.simulator = Simulator()
        self.simulator.reset()

    def test_initial_state(self):
        # Test the initial state of the simulator
        state = self.simulator._state
        self.assertEqual(state.cycle_count, 0)
        self.assertFalse(state.halted)

    def test_tick(self):
        # Test the tick method increments the cycle count
        initial_cycle_count = self.simulator._state.cycle_count
        self.simulator._state.tick()
        self.assertEqual(self.simulator._state.cycle_count, initial_cycle_count + 1)

    def test_reset(self):
        # Test resetting the simulator
        self.simulator._state.tick()
        self.simulator.reset()
        state = self.simulator._state
        self.assertEqual(state.cycle_count, 0)
        self.assertFalse(state.halted)


if __name__ == "__main__":
    unittest.main()
