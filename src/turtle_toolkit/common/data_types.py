"""data_types.py - Common data types for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from typing import ClassVar, Self

from turtle_toolkit.common.config import (
    DATA_ADDRESS_WIDTH,
    DATA_WIDTH,
    INSTRUCTION_ADDRESS_WIDTH,
)


@dataclass(frozen=True)
class BusValue:
    """Class representing a bus data type.

    Attributes:
        data (int): The data value of the bus.
    """

    value: int
    _bus_width: ClassVar[int] = DATA_WIDTH

    def __post_init__(self):
        """Post-initialization to ensure value is within bounds."""
        # Ensure the value is within the union of signed and unsigned ranges
        if not (self.min_signed_value() <= self.value <= self.max_unsigned_value()):
            raise ValueError(f"Value {self.value} is out of bounds for bus data type.")
        object.__setattr__(self, "value", self.value % (2**self._bus_width))

    def bit_length(self) -> int:
        """Return the bit length of the data."""
        return self._bus_width

    def unsigned_value(self) -> int:
        """Return the unsigned value of the bus data."""
        return self.value % (2**self._bus_width)

    def signed_value(self) -> int:
        """Return the signed value of the bus data."""
        if self.unsigned_value() > self.max_signed_value():
            return self.unsigned_value() - 2**self._bus_width
        return self.unsigned_value()

    def is_negative(self) -> bool:
        """Check if the bus data is negative."""
        return self.signed_value() < 0

    def get_slice(self, start: int, end: int) -> Self:
        """Return a slice of the bus data."""
        if start < 0 or end > self._bus_width or start >= end:
            raise ValueError("Invalid slice indices.")
        mask = (1 << (end - start)) - 1
        sliced_value = (self.unsigned_value() >> start) & mask
        return self.__class__(sliced_value)

    @staticmethod
    def min_unsigned_value() -> int:
        """Return the minimum value of the bus data."""
        return 0

    @classmethod
    def max_unsigned_value(cls: type[Self]) -> int:
        """Return the maximum value of the bus data."""
        return 2**cls._bus_width - 1

    @classmethod
    def min_signed_value(cls: type[Self]) -> int:
        """Return the minimum signed value of the bus data."""
        return -(2 ** (cls._bus_width - 1))

    @classmethod
    def max_signed_value(cls: type[Self]) -> int:
        """Return the maximum signed value of the bus data."""
        return 2 ** (cls._bus_width - 1) - 1

    def __add__(self, other: Self) -> Self:
        """Add two DataBusValue objects."""
        return self.__class__(
            (self.unsigned_value() + other.unsigned_value()) % (2**self._bus_width)
        )

    def __sub__(self, other: Self) -> Self:
        """Subtract two DataBusValue objects."""
        return self.__class__(
            (self.unsigned_value() - other.unsigned_value()) % (2**self._bus_width)
        )

    def __and__(self, other: Self) -> Self:
        """Bitwise AND of two DataBusValue objects."""
        return self.__class__(self.unsigned_value() & other.unsigned_value())

    def __or__(self, other: Self) -> Self:
        """Bitwise OR of two DataBusValue objects."""
        return self.__class__(self.unsigned_value() | other.unsigned_value())

    def __xor__(self, other: Self) -> Self:
        """Bitwise XOR of two DataBusValue objects."""
        return self.__class__(self.unsigned_value() ^ other.unsigned_value())

    def __invert__(self) -> Self:
        """Bitwise NOT of the DataBusValue object."""
        inverted_value = ~self.unsigned_value() & self.max_unsigned_value()
        return self.__class__(inverted_value)

    def __str__(self) -> str:
        """String representation of the DataBusValue object."""
        return (
            "DataBusValue("
            + f"value={self.value}, "
            + f"unsigned={self.unsigned_value()}, "
            + f"signed={self.signed_value()}, "
            + f"binary={self.to_binary()})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality of two DataBusValue objects or a DataBusValue and an int."""
        if isinstance(other, BusValue):
            return self.unsigned_value() == other.unsigned_value()
        else:
            return self.unsigned_value() == other

    def to_binary(self) -> str:
        """Return the binary representation of the DataBusValue object."""
        return format(self.unsigned_value(), f"0{self._bus_width}b")


class DataBusValue(BusValue):
    """Class representing a data bus value.

    Inherits from BusValue and adds additional functionality
    specific to data buses.
    """

    pass


class InstructionAddressBusValue(BusValue):
    """Class representing an instruction address bus value.

    Inherits from BusValue and adds additional functionality
    specific to instruction address buses.
    """

    _bus_width: ClassVar[int] = INSTRUCTION_ADDRESS_WIDTH


class DataAddressBusValue(BusValue):
    """Class representing a data address bus value.

    Inherits from BusValue and adds additional functionality
    specific to data address buses.
    """

    _bus_width: ClassVar[int] = DATA_ADDRESS_WIDTH
