"""Tests for the InvariantDict class."""

import pytest

from invariant.custom_types.invariant_bool import InvariantBool
from invariant.custom_types.invariant_dict import InvariantDict
from invariant.testing import LambdaMatcher


def test_invariant_dict_str():
    """Test the string representation of InvariantDict."""
    dict1 = InvariantDict({"hello": 1}, address=["addr1"])
    assert str(dict1) == "InvariantDict{'hello': 1} at ['addr1']"
    assert repr(dict1) == "InvariantDict{'hello': 1} at ['addr1']"


def test_invariant_dict_get():
    """Test the __getitem__ method of InvariantDict."""
    dict1 = InvariantDict({"hello": 1}, address=["addr1"])
    assert dict1["hello"] == 1
    assert dict1["world"] is None


def test_invariant_dict_matches():
    """Test the matches function in InvariantDict."""

    # Test case 1: Matching with a lambda that checks for specific keys
    matcher = LambdaMatcher(lambda d: "key1" in d and "key2" in d)
    value = {"key1": 1, "key2": 2, "key3": 3}
    addresses = ["address1"]
    invariant_dict = InvariantDict(value, addresses)

    result = invariant_dict.matches(matcher)
    assert isinstance(result, InvariantBool)
    assert result.value is True  # Should match since "key1" and "key2" exist
    assert result.addresses == ["address1"]

    # Test case 2: Matching with a lambda that checks for a missing key
    matcher = LambdaMatcher(lambda d: "missing_key" in d)
    result = invariant_dict.matches(matcher)
    assert isinstance(result, InvariantBool)
    assert result.value is False  # Should not match since "missing_key" doesn't exist
    assert result.addresses == ["address1"]

    # Test case 3: Matching with a lambda that checks for specific values
    matcher = LambdaMatcher(lambda d: d.get("key1") == 1 and d.get("key2") == 2)
    result = invariant_dict.matches(matcher)
    assert isinstance(result, InvariantBool)
    assert (
        result.value is True
    )  # Should match since key1 and key2 have the expected values
    assert result.addresses == ["address1"]

    # Test case 4: Matching with an empty dictionary
    matcher = LambdaMatcher(lambda d: len(d) == 0)
    empty_invariant_dict = InvariantDict({}, ["empty_address"])
    result = empty_invariant_dict.matches(matcher)
    assert isinstance(result, InvariantBool)
    assert result.value is True  # Should match since the dictionary is empty
    assert result.addresses == ["empty_address"]

    # Test case 5: Invalid matcher (not a Matcher instance)
    with pytest.raises(AttributeError):
        invariant_dict.matches("not_a_matcher")
