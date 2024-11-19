"""Test cases for the InvariantString class."""

import pytest
from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_string import InvariantString


def test_invariant_string_initialization():
    """Test initialization of InvariantString."""
    string = InvariantString("Hello", ["addr1"])
    assert string.value == "Hello"
    assert string.addresses == ["addr1:0-5"]

    # Test default addresses
    string = InvariantString("World")
    assert string.addresses == []

    # Test invalid value type
    with pytest.raises(TypeError, match="value must be a str"):
        InvariantString(123)

    # Test invalid addresses type
    with pytest.raises(TypeError, match="addresses must be a list of strings"):
        InvariantString("Hello", [1, 2, 3])


@pytest.mark.parametrize(
    "value1, value2, expected",
    [
        (InvariantString("Hello"), "Hello", True),
        (InvariantString("Hello"), "World", False),
        (InvariantString("Hello"), InvariantString("Hello"), True),
        (InvariantString("Hello"), InvariantString("World"), False),
    ],
)
def test_invariant_string_equality(value1, value2, expected):
    """Test equality of InvariantString objects."""
    result = value1 == value2
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value1, value2, expected",
    [
        (InvariantString("Hello"), "Hello", False),
        (InvariantString("Hello"), "World", True),
        (InvariantString("Hello"), InvariantString("Hello"), False),
        (InvariantString("Hello"), InvariantString("World"), True),
    ],
)
def test_invariant_string_inequality(value1, value2, expected):
    """Test inequality of InvariantString objects."""
    result = value1 != value2
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value, substring, expected",
    [
        (InvariantString("Hello World"), "World", True),
        (InvariantString("Hello World"), "world", False),  # Case-sensitive
        (InvariantString("Hello"), "Hell", True),
        (InvariantString("Hello"), "o", True),
        (InvariantString("Hello"), "Goodbye", False),
    ],
)
def test_invariant_string_contains(value, substring, expected):
    """Test the contains method of InvariantString."""
    result = value.contains(substring)
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value1, value2, expected_value, expected_addresses",
    [
        (InvariantString("Hello"), "World", "HelloWorld", []),
        (
            InvariantString("Hello", ["addr1"]),
            InvariantString("World", ["addr2"]),
            "HelloWorld",
            ["addr1:0-5", "addr2:0-5"],
        ),
        ("World", InvariantString("Hello", ["addr1"]), "WorldHello", ["addr1:0-5"]),
    ],
)
def test_invariant_string_concatenation(
    value1, value2, expected_value, expected_addresses
):
    """Test the concatenation of InvariantString objects."""
    result = value1 + value2
    assert isinstance(result, InvariantString)
    assert result.value == expected_value
    assert result.addresses == expected_addresses


def test_invariant_string_str_and_repr():
    """Test string representation of InvariantString."""
    string = InvariantString("Hello", ["addr1"])
    assert str(string) == "InvariantString(value=Hello, addresses=[addr1:0-5])"
    assert repr(string) == "InvariantString(value=Hello, addresses=[addr1:0-5])"
