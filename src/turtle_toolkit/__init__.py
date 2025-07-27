"""
Turtle Toolkit - Library API for Turtle CPU assembler, simulator, and tools
"""

from .assembler import Assembler
from .simulator import Simulator
from .main import assemble_file, simulate_binary, compare_memory_dumps

# Expose main library functions
__all__ = [
    'Assembler',
    'Simulator', 
    'assemble_file',
    'simulate_binary',
    'compare_memory_dumps',
    'assemble_program',
    'simulate_program',
    'compare_files'
]

def assemble_program(source_code: str, output_format: str = "binstr") -> bytes:
    """Assemble source code to binary format.
    
    Args:
        source_code: Assembly source code as string
        output_format: Output format - "bin", "binstr", "hexstr"
    
    Returns:
        Binary data as bytes
    """
    if output_format == "binstr":
        binary, _ = Assembler.assemble_to_binary_string(source_code, "inline", "stripped")
        return binary
    elif output_format == "hexstr":
        binary, _ = Assembler.assemble_to_hex_string(source_code, "inline", "stripped") 
        return binary
    else:  # "bin"
        return Assembler.assemble(source_code)

def simulate_program(binary: bytes, max_cycles: int = 10000, dump_memory: str = None, dump_registers: str = None) -> dict:
    """Simulate binary program and return results.
    
    Args:
        binary: Binary program data
        max_cycles: Maximum cycles to simulate
        dump_memory: Path to dump memory to (optional)
        dump_registers: Path to dump registers to (optional)
    
    Returns:
        Dict with simulation results including state dumps
    """
    simulator = Simulator()
    simulator.reset()
    simulator.load_binary(binary)
    
    result = simulator.run_until_halt(max_cycles)
    
    # Generate memory and register dumps
    memory_dump = simulator.get_data_memory_dump(dump_full_memory=True)
    register_dump = simulator.get_register_file_dump()
    
    # Write to files if requested
    if dump_memory:
        with open(dump_memory, 'w') as f:
            f.write(memory_dump)
    
    if dump_registers:
        with open(dump_registers, 'w') as f:
            f.write(register_dump)
    
    return {
        'cycle_count': result.cycle_count,
        'halted': result.state.halted,
        'memory_dump': memory_dump,
        'register_dump': register_dump,
        'final_state': result.state
    }

def compare_files(file1: str, file2: str, ignore_comments: bool = True, verbose: bool = False) -> bool:
    """Compare two memory/register dump files.
    
    Args:
        file1: Path to first file
        file2: Path to second file 
        ignore_comments: Whether to ignore comment lines
        verbose: Whether to show verbose output
    
    Returns:
        True if files match, False otherwise
    """
    from .main import compare_memory_dumps
    return compare_memory_dumps(file1, file2, ignore_comments, verbose)