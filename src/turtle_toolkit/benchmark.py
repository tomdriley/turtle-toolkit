"""benchmark.py - A module for benchmarking the performance of turtle simulator.
Author: Tom Riley
Date: 2025-05-14
"""

import time
from os import path

from turtle_toolkit.assembler import Assembler
from turtle_toolkit.common.logger import logger
from turtle_toolkit.main import read_text_file
from turtle_toolkit.simulator import Simulator

LOCAL_DIR = path.dirname(path.abspath(__file__))
EXAMPLES_DIR = path.join(LOCAL_DIR, "../../examples")
LARGE_MULTIPLICATION_ASM = path.join(EXAMPLES_DIR, "large_multiplication_benchmark.asm")


def _run_simulator(binary: bytes):
    simulator = Simulator()
    simulator.reset()
    simulator.load_binary(binary)
    return simulator.run_until_halt()


def benchmark_simulator():
    logger.info("Starting benchmark...")
    assembly_code = read_text_file(LARGE_MULTIPLICATION_ASM)
    binary = Assembler.assemble(assembly_code)
    num_runs = 10
    total_cycles = 0
    logger.disabled = True
    start_time = time.time()
    for _ in range(num_runs):
        result = _run_simulator(binary)
        total_cycles += result.cycle_count
    end_time = time.time()
    logger.disabled = False
    execution_time = end_time - start_time
    logger.info(f"Execution time: {execution_time:.2f} seconds for {num_runs} runs.")
    logger.info(
        f"Average execution time: {execution_time / num_runs:.2f} seconds per run."
    )
    logger.info(f"Total cycles executed: {total_cycles} cycles.")
    logger.info(
        f"Average cycles executed: {total_cycles / num_runs:.0f} cycles per run."
    )
    logger.info(
        f"Overall cycles simulated per second: {total_cycles / execution_time:.2f} cycles/s."
    )


if __name__ == "__main__":
    benchmark_simulator()
