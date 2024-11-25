"""Tests for the InvariantDict class."""

from invariant_runner.custom_types.invariant_dict import InvariantDict


def test_invariant_dict_str():
    """Test the string representation of InvariantDict."""
    dict1 = InvariantDict({"hello": 1}, address=["addr1"])
    assert str(dict1) == "InvariantDict{'hello': 1} at ['addr1']"
    assert repr(dict1) == "InvariantDict{'hello': 1} at ['addr1']"