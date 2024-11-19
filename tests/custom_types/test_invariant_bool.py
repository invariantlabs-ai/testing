"""Tests for the InvariantBool class."""

import pytest
from invariant_runner.custom_types.invariant_bool import InvariantBool


@pytest.mark.parametrize(
    "bool1, bool2, expected",
    [
        (InvariantBool(True), InvariantBool(True), True),
        (InvariantBool(True), True, True),
        (True, InvariantBool(True), True),
        (False, InvariantBool(True), False),
        (InvariantBool(True), False, False),
        (InvariantBool(False), False, True),
        (False, InvariantBool(False), True),
    ],
)
def test_invariant_bool_equality(bool1, bool2, expected):
    """Test the equality of InvariantBool objects."""
    assert (bool1 == bool2).value == expected


@pytest.mark.parametrize(
    "bool1, bool2, expected",
    [
        (InvariantBool(True), InvariantBool(False), True),
        (InvariantBool(True), False, True),
        (InvariantBool(True), True, False),
        (InvariantBool(False), True, True),
        (False, InvariantBool(True), True),
        (True, InvariantBool(False), True),
        (False, InvariantBool(False), False),
    ],
)
def test_invariant_bool_inequality(bool1, bool2, expected):
    """Test the inequality of InvariantBool objects."""
    assert (bool1 != bool2).value == expected


@pytest.mark.parametrize(
    "bool1, bool2, expected",
    [
        (InvariantBool(True), InvariantBool(False), False),
        (InvariantBool(True), InvariantBool(True), True),
        (InvariantBool(True), True, True),
        (InvariantBool(True), False, False),
        (False, InvariantBool(True), False),
        (True, InvariantBool(True), True),
    ],
)
def test_invariant_bool_and(bool1, bool2, expected):
    """Test the AND operation of InvariantBool objects."""
    assert (bool1 & bool2).value == expected


@pytest.mark.parametrize(
    "bool1, bool2, expected",
    [
        (InvariantBool(True), InvariantBool(False), True),
        (InvariantBool(False), InvariantBool(False), False),
        (InvariantBool(True), True, True),
        (InvariantBool(True), False, True),
        (False, InvariantBool(True), True),
        (True, InvariantBool(True), True),
    ],
)
def test_invariant_bool_or(bool1, bool2, expected):
    """Test the OR operation of InvariantBool objects."""
    assert (bool1 | bool2).value == expected


@pytest.mark.parametrize(
    "bool1, expected",
    [
        (InvariantBool(True), False),
        (InvariantBool(False), True),
    ],
)
def test_invariant_bool_not(bool1, expected):
    """Test the NOT operation of InvariantBool objects."""
    assert (~bool1).value == expected


def test_invariant_bool_with_addresses():
    """Test the InvariantBool objects with addresses."""
    bool1 = InvariantBool(True, addresses=["address1"])
    bool2 = InvariantBool(True, addresses=["address1"])
    bool3 = InvariantBool(False, addresses=["address2"])
    assert bool1 == bool2
    assert bool1 != bool3
    assert bool1 == True  # noqa: E712 pylint: disable=singleton-comparison
    assert bool1 != False  # noqa: E712 pylint: disable=singleton-comparison
    assert bool1.addresses == ["address1"]
    assert bool3.addresses == ["address2"]
