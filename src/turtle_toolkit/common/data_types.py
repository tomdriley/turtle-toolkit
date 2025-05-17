"""data_types.py - Common data types for the simulator
Author: Tom Riley
Date: 2025-05-04
"""

from dataclasses import dataclass
from typing import ClassVar, Self

import numpy as np

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

    value: np.uint16
    BUS_WIDTH: ClassVar[np.uint16] = np.uint16(DATA_WIDTH)
    BUS_WIDTH_MASK: ClassVar[np.uint16] = np.uint16((1 << DATA_WIDTH) - 1)
    SIGN_BIT_MASK: ClassVar[np.uint16] = np.uint16(1 << (DATA_WIDTH - 1))
    MIN_UNSIGNED_VALUE: ClassVar[np.uint16] = np.uint16(0)
    MAX_UNSIGNED_VALUE: ClassVar[np.uint16] = BUS_WIDTH_MASK
    MIN_SIGNED_VALUE: ClassVar[np.int16] = np.int16(SIGN_BIT_MASK)
    MAX_SIGNED_VALUE: ClassVar[np.int16] = MIN_SIGNED_VALUE - np.int16(1)

    def __post_init__(self):
        """Post-initialization to ensure value is within bounds."""
        # Ensure the value is within the union of signed and unsigned ranges
        if not (self.MIN_SIGNED_VALUE <= self.value <= self.MAX_UNSIGNED_VALUE):
            raise ValueError(f"Value {self.value} is out of bounds for bus data type.")
        object.__setattr__(self, "value", np.uint16(self.value & self.BUS_WIDTH_MASK))

    def bit_length(self) -> np.uint16:
        """Return the bit length of the data."""
        return self.BUS_WIDTH

    def unsigned_value(self) -> np.uint16:
        """Return the unsigned value of the bus data."""
        return self.value & self.BUS_WIDTH_MASK

    def signed_value(self) -> np.int16:
        """Return the signed value of the bus data."""
        val = self.unsigned_value()
        return np.int16((self.SIGN_BIT_MASK ^ val) - self.SIGN_BIT_MASK)

    def is_negative(self) -> np.bool:
        """Check if the bus data is negative."""
        return self.signed_value() < 0

    def get_slice(self, start: np.uint16, end: np.uint16) -> Self:
        """Return a slice of the bus data."""
        if start < 0 or end > self.BUS_WIDTH or start >= end:
            raise ValueError("Invalid slice indices.")
        mask: np.uint16 = (1 << (end - start)) - np.uint16(1)
        sliced_value = (self.unsigned_value() >> start) & mask
        return self.__class__(sliced_value)

    def __add__(self, other: Self) -> Self:
        """Add two DataBusValue objects."""
        return self.__class__(
            (self.unsigned_value() + other.unsigned_value()) & self.BUS_WIDTH_MASK
        )

    def __sub__(self, other: Self) -> Self:
        """Subtract two DataBusValue objects."""
        return self.__class__(
            (self.unsigned_value() - other.unsigned_value()) & self.BUS_WIDTH_MASK
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
        inverted_value = ~self.unsigned_value() & self.MAX_UNSIGNED_VALUE
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

    def __lt__(self, other: object) -> bool:
        """Throw an error if directly comparing since we don't know if they are signed or unsigned."""
        raise NotImplementedError(
            "Direct comparison of BusValue objects is not supported. "
        )

    def __le__(self, other: object) -> bool:
        """Throw an error if directly comparing since we don't know if they are signed or unsigned."""
        raise NotImplementedError(
            "Direct comparison of BusValue objects is not supported. "
        )

    def __gt__(self, other: object) -> bool:
        """Throw an error if directly comparing since we don't know if they are signed or unsigned."""
        raise NotImplementedError(
            "Direct comparison of BusValue objects is not supported. "
        )

    def __ge__(self, other: object) -> bool:
        """Throw an error if directly comparing since we don't know if they are signed or unsigned."""
        raise NotImplementedError(
            "Direct comparison of BusValue objects is not supported. "
        )

    def to_binary(self) -> str:
        """Return the binary representation of the DataBusValue object."""
        return format(self.unsigned_value(), f"0{self.BUS_WIDTH}b")


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

    BUS_WIDTH: ClassVar[np.uint16] = np.uint16(INSTRUCTION_ADDRESS_WIDTH)


class DataAddressBusValue(BusValue):
    """Class representing a data address bus value.

    Inherits from BusValue and adds additional functionality
    specific to data address buses.
    """

    BUS_WIDTH: ClassVar[np.uint16] = np.uint16(DATA_ADDRESS_WIDTH)
