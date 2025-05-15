# 🐢 Turtle Toolkit 🔨

Turtle Toolkit is a comprehensive toolchain for simulating and assembling programs for a 8-bit TTL-based CPU. It provides a command-line interface (CLI) for assembling assembly code into binary, simulating the binary on a CPU simulator, and performing both tasks in one step.

---

## Installation

For development: 

```bash
poetry install
```

For using the tool:

```bash
pipx install . --python python3.11
```

---

## Running Tests

The project includes an extensive test suite to validate its functionality.

```bash
poetry run pytest
```

---

## Running Benchmarks

The project includes an benchmark to measure the performance of the simulator.

```bash
poetry run benchmark
```

---

## Example Usage

### Assemble Example

To assemble an assembly source file (`examples/load_store_different_address.asm`) into a binary file (`program.bin`):
```bash
   poetry run turtle-toolkit assemble examples/load_store_different_address.asm -o program.bin
```

### Simulate Example

To simulate a binary file (`program.bin`) with a maximum of 5000 cycles:
```bash
   poetry run turtle-toolkit simulate program.bin -m 5000
```

### Run Example

To assemble and simulate an assembly source file (`program.asm`) in one step:
```bash
   poetry run turtle-toolkit run examples/load_store_different_address.asm -m 5000
```

---

## Usage

### CLI Commands

The Turtle Toolkit provides the following CLI commands:

1. **Assemble**: Assemble assembly source code into binary.
   ```bash
   poetry run turtle-toolkit assemble <input_file> [-o <output_file>] [-v]
   ```
   - `input_file`: Path to the assembly source file.
   - `-o, --output`: (Optional) Path to save the output binary file.
   - `-v, --verbose`: Enable verbose output.

2. **Simulate**: Simulate a binary file on the CPU simulator.
   ```bash
   poetry run turtle-toolkit simulate <input_file> [-m <max_cycles>] [-v]
   ```
   - `input_file`: Path to the binary file to simulate.
   - `-m, --max-cycles`: (Optional) Maximum number of cycles to simulate (default: 10000).
   - `-v, --verbose`: Enable verbose output.

3. **Run**: Assemble and simulate in one step.
   ```bash
   poetry run turtle-toolkit run <input_file> [-o <output_file>] [-m <max_cycles>] [-v]
   ```
   - `input_file`: Path to the assembly source file.
   - `-o, --output`: (Optional) Path to save the intermediate binary file.
   - `-m, --max-cycles`: (Optional) Maximum number of cycles to simulate (default: 10000).
   - `-v, --verbose`: Enable verbose output.

---

## Author

Tom Riley 2025