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

    def test_run_for_fixed_cycles(self):
        # Test running the simulator for a fixed number of cycles
        num_cycles = 5
        states = list(self.simulator.run(num_cycles))
        self.assertEqual(len(states), num_cycles)
        self.assertEqual(self.simulator._state.cycle_count, num_cycles)

    def test_halt_simulation(self):
        # Test halting the simulation
        self.simulator._state.halted = True
        states = list(self.simulator.run(10))
        self.assertEqual(len(states), 0)
        self.assertEqual(self.simulator._state.cycle_count, 1)

    def test_reset(self):
        # Test resetting the simulator
        self.simulator._state.tick()
        self.simulator.reset()
        state = self.simulator._state
        self.assertEqual(state.cycle_count, 0)
        self.assertFalse(state.halted)


if __name__ == "__main__":
    unittest.main()
