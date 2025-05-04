# main.py
# This is the main entry point for the simulator.
# author: Tom Riley
# date: 2025-05-04

from simulator.add import add

if __name__ == "__main__":
    a = 5
    b = 10
    result = add(a, b)
    print(f"The sum of {a} and {b} is {result}.")
    print("Hello, World!")
