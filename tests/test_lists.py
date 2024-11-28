"""Tests for the invariant list functions."""

import pytest

import invariant.testing.functional as F
from invariant.custom_types.invariant_bool import InvariantBool
from invariant.custom_types.invariant_number import InvariantNumber
from invariant.custom_types.invariant_string import InvariantString
from invariant.testing import Trace


@pytest.fixture(name="message_list")
def fixture_message_list():
    """Returns a list of messages."""
    trace = Trace(
        trace=[
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "Hi, how can I help you?"},
            {"role": "user", "content": "I need help with something."},
            {"role": "assistant", "content": "Sure, what do you need help with?"},
            {"role": "user", "content": "I need help with my computer."},
            {"role": "assistant", "content": "Okay, what seems to be the problem?"},
            {"role": "user", "content": "It won't turn on."},
            {"role": "assistant", "content": "Have you tried plugging it in?"},
            {"role": "user", "content": "Oh, that worked. Thanks!"},
        ]
    )
    return trace.messages()


@pytest.fixture(name="invariant_number_list")
def fixture_invariant_number_list():
    """Returns a list of InvariantNumber objects."""
    return [
        InvariantNumber(1, addresses=["0"]),
        InvariantNumber(5, addresses=["1"]),
        InvariantNumber(8, addresses=["2"]),
    ]


@pytest.fixture(name="invariant_string_list")
def fixture_invariant_string_list():
    """Returns a list of InvariantString objects."""
    return [
        InvariantString("1", addresses=["0"]),
        InvariantString("12", addresses=["1"]),
        InvariantString("123", addresses=["2"]),
    ]


@pytest.fixture(name="invariant_bool_list")
def fixture_invariant_bool_list():
    """Returns a list of InvariantBool objects."""
    return [
        InvariantBool(True, addresses=["0"]),
        InvariantBool(False, addresses=["1"]),
        InvariantBool(True, addresses=["2"]),
    ]


def test_list_index_access(message_list: list):
    """Test that we can access elements in the list by index."""
    assert message_list[1]["content"].value == "Hi, how can I help you?"


def test_list_length(message_list: list):
    """Test that the list has the correct length."""
    assert len(message_list) == 9


def test_list_iteration(message_list: list):
    """Test that we can iterate over the list."""
    for i, message in enumerate(message_list):
        assert message["content"].value == message_list[i]["content"].value


def test_map_applies_function(message_list: list):
    """Test that the map function applies a function to each element in the list."""
    test_message_content = message_list[1]["content"].value
    new_list = F.map(lambda item: item["content"] == test_message_content, message_list)

    for i, new_item in enumerate(new_list):
        assert new_item.value == (
            message_list[i]["content"].value == test_message_content
        )


def test_map_maintains_addresses(message_list: list):
    """Test that the map function maintains addresses when applying a function."""
    new_list = F.map(lambda item: item, message_list)

    for i, new_item in enumerate(new_list):
        assert new_item.addresses == message_list[i].addresses


def test_reduce(invariant_number_list: list):
    """Test that the reduce function works."""
    sum_of_list = 0
    for item in invariant_number_list:
        sum_of_list += item.value

    reduced = F.reduce(lambda a, b: a + b, 0, invariant_number_list)

    assert reduced.value == sum_of_list
    assert isinstance(reduced, InvariantNumber)


def test_reduce_raw(invariant_number_list: list):
    """Test that the reduce_raw returns the correct value and removes address information."""
    sum_of_list = 0
    for item in invariant_number_list:
        sum_of_list += item.value

    reduced = F.reduce_raw(lambda a, b: a + b, 0, invariant_number_list)

    assert reduced == sum_of_list
    assert isinstance(reduced, int)


def test_min_helper(invariant_number_list: list):
    """Test that the min helper correct value and only keeps one address."""
    min_of_list = min([item.value for item in invariant_number_list])
    min_value = min(invariant_number_list)

    assert min_value.value == min_of_list
    assert len(min_value.addresses) == 1


def test_max_helper(invariant_number_list: list):
    """Test that the max helper returns correct value and only keeps one address."""
    max_of_list = max([item.value for item in invariant_number_list])

    max_value = max(invariant_number_list)

    assert max_value.value == max_of_list
    assert len(max_value.addresses) == 1


def test_sum_helper(invariant_number_list: list):
    """Test that the sum helper returns correct value and keeps all addresses."""
    sum_of_list = sum([item.value for item in invariant_number_list])
    sum_value = sum(invariant_number_list)

    assert isinstance(sum_value, InvariantNumber)
    assert sum_value.value == sum_of_list
    assert len(sum_value.addresses) == len(invariant_number_list)


def test_count_helper(invariant_string_list: list):
    """Test that the count helper returns correct value and keeps all addresses."""
    string_to_count = "12"

    count_value = F.count(string_to_count, invariant_string_list)
    real_count = sum(
        [1 if item.value == string_to_count else 0 for item in invariant_string_list]
    )

    assert isinstance(count_value, InvariantNumber)
    assert count_value.value == real_count
    assert len(count_value.addresses) == len(invariant_string_list)


def test_any_helper(invariant_bool_list: list):
    """Test that the any helper returns correct value and keeps all addresses."""
    any_value = F.any(invariant_bool_list)

    assert isinstance(any_value, InvariantBool)
    assert any_value.value == True
    assert len(any_value.addresses) == len(invariant_bool_list)


def test_all_helper(invariant_bool_list: list):
    """Test that the all helper returns correct value and keeps all addresses."""
    all_value = F.all(invariant_bool_list)

    assert isinstance(all_value, InvariantBool)
    assert all_value.value == False
    assert len(all_value.addresses) == len(invariant_bool_list)


def test_invariant_filter():
    """Test the invariant_filter function."""
    values = [
        InvariantNumber(1, addresses=["addr1"]),
        InvariantNumber(2, addresses=["addr2"]),
        InvariantNumber(3, addresses=["addr3"]),
    ]
    result = F.filter(lambda x: x.value > 1, values)
    assert result == [InvariantNumber(2), InvariantNumber(3)]


def test_invariant_find():
    """Test the invariant_find function."""
    values = [InvariantNumber(1), InvariantNumber(2), InvariantNumber(3)]
    result = F.find(lambda x: x.value > 1, values)
    assert result == InvariantNumber(2)

    result = F.find(lambda x: x.value > 3, values)
    assert result is None

    values = [
        InvariantString("abc"),
        InvariantString("def", addresses=["addr1"]),
        InvariantString("ghi"),
    ]
    result = F.find(lambda x: x.value == "def", values)
    assert result.value == "def"
    assert result.addresses == ["addr1:0-3"]


def test_invariant_min():
    """Test the invariant_min function."""
    values = [InvariantNumber(3), InvariantNumber(1), InvariantNumber(2)]
    result = F.min(values)
    assert result == InvariantNumber(1)


def test_invariant_max():
    """Test the invariant_max function."""
    values = [InvariantNumber(3), InvariantNumber(1), InvariantNumber(2)]
    result = F.max(values)
    assert result == InvariantNumber(3)
