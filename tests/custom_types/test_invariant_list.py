"""Tests for the InvariantList class."""

import pytest
from invariant_runner.custom_types.invariant_list import InvariantList
from invariant_runner.custom_types.invariant_string import InvariantString


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


def test_invariant_list_getitem():
    """Test the getitem method of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=[["addr1"], ["addr2"]])
    assert list1[0] == InvariantString("hello", addresses=["addr1"])
    assert list1[1] == InvariantString("bye", addresses=["addr2"])


def test_invariant_list_iter():
    """Test the iter method of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=[["addr1"], ["addr2"]])
    for i, item in enumerate(list1):
        assert item == list1[i]


def test_invariant_list_from_values():
    """Test the from_values method of InvariantList."""
    list1 = InvariantList.from_values([InvariantString(
        "hello", addresses=["addr1"]), InvariantString("bye", addresses=["addr2"])])
    assert list1 == InvariantList(
        ["hello", "bye"], addresses=[["addr1:0-5"], ["addr2:0-3"]])


def test_invariant_list_eq():
    """Test the eq method of InvariantList."""
    list1 = InvariantList(["hello", "bye"], addresses=[["addr1"], ["addr2"]])
    list2 = InvariantList(["hello", "bye"], addresses=[["addr1"], ["addr2"]])
    assert list1 == list2

    with pytest.raises(TypeError):
        list1 == "hello"
