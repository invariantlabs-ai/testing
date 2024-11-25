"""Tests for the InvariantList class."""

from invariant_runner.custom_types.invariant_list import InvariantList


def test_invariant_list_str():
    """Test the string representation of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=["addr1"])
    assert str(list1) == "InvariantList['hello', 'bye'] at ['addr1']"
    assert repr(list1) == "InvariantList['hello', 'bye'] at ['addr1']"

    list2 = InvariantList([1], addresses=[])
    assert str(list2) == "InvariantList[1] at []"
    assert repr(list2) == "InvariantList[1] at []"

def test_invariant_list_contains():
    """Test the string representation of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=["addr1"])
    assert "hello" in list1
    assert "bye" in list1
    assert "hi" not in list1