import unittest
from simulator.simulator import (
    Simulator,
    DATA_MEMORY_NAME,
    INSTRUCTION_MEMORY_NAME,
    PROGRAM_COUNTER_NAME,
    REGISTER_FILE_NAME,
)
from simulator.common.config import INSTRUCTION_WIDTH
from simulator.modules.instruction_memory import INSTRUCTION_FETCH_LATENCY_CYCLES
from simulator.assembler import Assembler
from simulator.common.data_types import DataBusValue
from simulator.modules.register_file import RegisterIndex


class TestSimulator(unittest.TestCase):
    def setUp(self):
        # Ensure the simulator is reset before each test
        self.simulator = Simulator()
        self.simulator.reset()

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

    def test_set(self):
        # Test the set instruction
        source = """
        SET 1
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_load_program(self):
        # Test loading a program without assembling first
        source = """
        SET 1
        HALT
        """
        self.simulator.load_program(source)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_addi_instruction(self):
        # Test the ADD instruction
        source = """
        SET 1
        ADDI 2
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(3),
        )

    def test_put_instruction(self):
        # Test the PUT instruction
        source = """
        SET 1
        PUT R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.R0],
            DataBusValue(1),
        )

    def test_get_instruction(self):
        # Test the GET instruction
        source = """
        SET 1
        PUT R0
        SET 0
        GET R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_add_instruction(self):
        # Test the ADD instruction
        source = """
        SET 1
        PUT R0
        SET 2
        ADD R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(3),
        )

    def test_sub_instruction(self):
        # Test the SUB instruction
        source = """
        SET 3
        PUT R0
        SET 5
        SUB R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(2),
        )

    def test_and_instruction(self):
        # Test the AND instruction
        source = """
        SET 6  ; 0b0110
        PUT R0
        SET 5  ; 0b0101
        AND R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(4),  # 0b0100
        )

    def test_or_instruction(self):
        # Test the OR instruction
        source = """
        SET 2  ; 0b0010
        PUT R0
        SET 4  ; 0b0100
        OR R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(6),  # 0b0110
        )

    def test_xor_instruction(self):
        # Test the XOR instruction
        source = """
        SET 6  ; 0b0110
        PUT R0
        SET 3  ; 0b0011
        XOR R0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(5),  # 0b0101
        )

    def test_inv_instruction(self):
        # Test the INV instruction
        source = """
        SET 0b00001111
        INV
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0b11110000),
        )

    def test_subi_instruction(self):
        # Test the SUBI instruction
        source = """
        SET 5
        SUBI 2
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(3),
        )

    def test_andi_instruction(self):
        # Test the ANDI instruction
        source = """
        SET 0b0110
        ANDI 0b0101
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0b0100),
        )

    def test_ori_instruction(self):
        # Test the ORI instruction
        source = """
        SET 0b0010
        ORI 0b0100
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0b0110),
        )

    def test_xori_instruction(self):
        # Test the XORI instruction
        source = """
        SET 0b0110
        XORI 0b0011
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0b0101),
        )

    def test_jmpi_instruction(self):
        # Test the JMPI instruction
        source = """
        SET 0
        JMPI 4
        SET 1
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )

    def test_bz_instruction_taken(self):
        # Test the BZ instruction
        source = """
        SET 0
        BZ 4
        SET 1
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )

    def test_bz_instruction_not_taken(self):
        # Test the BZ instruction
        source = """
        SET 1
        BZ 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )

    def test_bnz_instruction_taken(self):
        # Test the BNZ instruction
        source = """
        SET 1
        BNZ 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_bnz_instruction_not_taken(self):
        # Test the BNZ instruction
        source = """
        SET 0
        BNZ 4
        SET 1
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_bp_instruction_taken(self):
        # Test the BP instruction
        source = """
        SET 1
        BP 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_bp_instruction_not_taken(self):
        # Test the BP instruction
        source = """
        SET -1
        BP 4
        SET 1
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(1),
        )

    def test_bn_instruction_taken(self):
        # Test the BN instruction
        source = """
        SET -1
        BN 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(-1),
        )

    def test_bn_instruction_not_taken(self):
        # Test the BN instruction
        source = """
        SET 1
        BN 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )

    def test_bcs_instruction_taken(self):
        # Test the Brabch if Carry Set (BCS) instruction
        source = """
        SET 0xFF
        ADDI 6
        BCS 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(5),
        )

    def test_bcs_instruction_not_taken(self):
        # Test the Branch if Carry Set (BCS) instruction
        source = """
        SET 0xFE
        ADDI 1
        BCS 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )

    def test_bcc_instruction_taken(self):
        # Test the Branch if Carry Clear (BCC) instruction
        source = """
        SET 0xFE
        ADDI 1
        BCC 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0xFF),
        )

    def test_bcc_instruction_not_taken(self):
        # Test the Branch if Carry Clear (BCC) instruction
        source = """
        SET 0xFF
        ADDI 6
        BCC 4
        SET 0
        HALT
        """
        binary = Assembler.assemble(source)
        self.simulator.load_binary(binary)
        self.simulator.run_until_halt()
        state = self.simulator.get_state()
        self.assertEqual(
            state.modules[REGISTER_FILE_NAME].registers[RegisterIndex.ACC],
            DataBusValue(0),
        )
