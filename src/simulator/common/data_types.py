"""data_types.py - Common data types for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from simulator.common.config import DATA_WIDTH


@dataclass(frozen=True)
class BusData:
    """Class representing a bus data type.

    Attributes:
        data (int): The data value of the bus.
    """

    value: int

    def __post_init__(self):
        """Post-initialization to ensure value is within bounds."""
        # Ensure the value is within the union of signed and unsigned ranges
        if not (self.min_signed_value() <= self.value <= self.max_unsigned_value()):
            raise ValueError(f"Value {self.value} is out of bounds for bus data type.")
        object.__setattr__(self, "value", self.value % (2**DATA_WIDTH))

    def bit_length(self) -> int:
        """Return the bit length of the data."""
        return DATA_WIDTH

    def unsigned_value(self) -> int:
        """Return the unsigned value of the bus data."""
        return self.value % (2**DATA_WIDTH)

    def signed_value(self) -> int:
        """Return the signed value of the bus data."""
        if self.unsigned_value() > self.max_signed_value():
            return self.unsigned_value() - 2**DATA_WIDTH
        return self.unsigned_value()

    def is_negative(self) -> bool:
        """Check if the bus data is negative."""
        return self.signed_value() < 0

    @staticmethod
    def min_unsigned_value() -> int:
        """Return the minimum value of the bus data."""
        return 0

    @staticmethod
    def max_unsigned_value() -> int:
        """Return the maximum value of the bus data."""
        return 2**DATA_WIDTH - 1

    @staticmethod
    def min_signed_value() -> int:
        """Return the minimum signed value of the bus data."""
        return -(2 ** (DATA_WIDTH - 1))

    @staticmethod
    def max_signed_value() -> int:
        """Return the maximum signed value of the bus data."""
        return 2 ** (DATA_WIDTH - 1) - 1

    def __add__(self, other: "BusData") -> "BusData":
        """Add two BusData objects."""
        return BusData(
            (self.unsigned_value() + other.unsigned_value()) % (2**DATA_WIDTH)
        )

    def __sub__(self, other: "BusData") -> "BusData":
        """Subtract two BusData objects."""
        return BusData(
            (self.unsigned_value() - other.unsigned_value()) % (2**DATA_WIDTH)
        )
