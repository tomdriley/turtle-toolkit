import numpy as np

from turtle_toolkit.common.data_types import (
    BusValue,
    DataAddressBusValue,
    DataBusValue,
    InstructionAddressBusValue,
)


def test_bus_value_unsigned():
    value = BusValue(np.uint16(10))
    assert value.unsigned_value() == 10
    assert value.signed_value() == 10
    assert not value.is_negative()


def test_bus_value_signed():
    value = BusValue(np.int16(-5))
    assert value.signed_value() == -5
    assert value.is_negative()


def test_bus_value_bit_length():
    value = BusValue(np.uint16(10))
    assert value.bit_length() == 8


def test_bus_value_get_slice():
    value = BusValue(np.uint16(0b11110000))
    sliced = value.get_slice(4, 8)
    assert sliced.unsigned_value() == 0b1111


def test_bus_value_addition():
    value1 = BusValue(np.uint16(5))
    value2 = BusValue(np.uint16(10))
    result = value1 + value2
    assert result.unsigned_value() == 15


def test_bus_value_subtraction():
    value1 = BusValue(np.int16(10))
    value2 = BusValue(np.int16(5))
    result = value1 - value2
    assert result.signed_value() == 5


def test_bus_value_bitwise_operations():
    value1 = BusValue(np.uint16(0b1010))
    value2 = BusValue(np.uint16(0b1100))
    assert (value1 & value2).unsigned_value() == 0b1000
    assert (value1 | value2).unsigned_value() == 0b1110
    assert (value1 ^ value2).unsigned_value() == 0b0110
    assert (~value1).unsigned_value() == 0b11110101


def test_data_bus_value():
    value = DataBusValue(np.uint16(255))
    assert value.unsigned_value() == 255
    assert value.signed_value() == -1


def test_instruction_address_bus_value():
    value = InstructionAddressBusValue(np.uint16(1024))
    assert value.unsigned_value() == 1024


def test_data_address_bus_value():
    value = DataAddressBusValue(np.uint16(512))
    assert value.unsigned_value() == 512


def test_data_bus_value_signed_behavior_positive():
    positive_value = DataBusValue(np.uint16(1))
    assert positive_value.signed_value() == 1
    assert not positive_value.is_negative()


def test_data_bus_value_signed_behavior_zero():
    zero_value = DataBusValue(np.uint16(0))
    assert zero_value.signed_value() == 0
    assert not zero_value.is_negative()


def test_data_bus_value_signed_behavior_max_positive():
    max_positive_value = DataBusValue(np.uint16(0x7F))
    assert max_positive_value.signed_value() == np.int16(0x7F)
    assert not max_positive_value.is_negative()


def test_data_bus_value_signed_behavior_negative():
    negative_value = DataBusValue(np.uint16(0xFF))
    assert negative_value.signed_value() == -1
    assert negative_value.is_negative()


def test_data_bus_value_signed_behavior_min_negative():
    min_negative_value = DataBusValue(np.uint16(0x80))
    assert min_negative_value.signed_value() == -0x80
    assert min_negative_value.is_negative()
