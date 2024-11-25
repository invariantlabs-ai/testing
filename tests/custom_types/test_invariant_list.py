"""Tests for the InvariantList class."""

import pytest
from invariant_runner.custom_types.invariant_list import InvariantList


def test_invariant_list_str():
    """Test the string representation of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=["addr1"])
    assert str(list1) == "InvariantList['hello', 'bye'] at ['addr1']"
    assert repr(list1) == "InvariantList['hello', 'bye'] at ['addr1']"

    list2 = InvariantList([{"key": "value"}], addresses=[])
    assert str(list2) == "InvariantList[\n  {'key': 'value'}\n] at []"
    assert repr(list2) == "InvariantList[\n  {'key': 'value'}\n] at []"

def test_invariant_list_contains():
    """Test the string representation of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=["addr1"])
    assert "hello" in list1
    assert "bye" in list1
    assert "hi" not in list1

def test_invariant_list_len():
    """Test the len method of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=["addr1"])
    assert list1.len() == 2

    with pytest.raises(NotImplementedError):
        len(list1)