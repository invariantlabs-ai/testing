"""Tests for the invariant_runner module."""

import pytest

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_list import *
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_string import InvariantString
from invariant_runner.custom_types.trace import Trace


@pytest.fixture
def message_list():
    trace = Trace(trace=[
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "Hi, how can I help you?"},
        {"role": "user", "content": "I need help with something."},
        {"role": "assistant", "content": "Sure, what do you need help with?"},
        {"role": "user", "content": "I need help with my computer."},
        {"role": "assistant", "content": "Okay, what seems to be the problem?"},
        {"role": "user", "content": "It won't turn on."},
        {"role": "assistant", "content": "Have you tried plugging it in?"},
        {"role": "user", "content": "Oh, that worked. Thanks!"},
    ])
    return trace.messages()


@pytest.fixture
def invariant_number_list():
    return [
        InvariantNumber(1, addresses=["0"]),
        InvariantNumber(5, addresses=["1"]),
        InvariantNumber(8, addresses=["2"]),
    ]

@pytest.fixture
def invariant_string_list():
    return [
        InvariantString('1', addresses=["0"]),
        InvariantString('12', addresses=["1"]),
        InvariantString('123', addresses=["2"]),
    ]


@pytest.fixture
def invariant_bool_list():
    return [
        InvariantBool(True, addresses=["0"]),
        InvariantBool(False, addresses=["1"]),
        InvariantBool(True, addresses=["2"]),
    ]


def test_list_index_access(message_list: list):
    assert message_list[1]["content"].value == "Hi, how can I help you?"

def test_list_length(message_list: list):
    assert len(message_list) == 9

def test_list_iteration(message_list: list):
    for i, message in enumerate(message_list):
        assert message["content"].value == message_list[i]["content"].value

def test_map_applies_function(message_list: list):
    # make sure the map function is correctly applied to every element in an list
    test_message_content = message_list[1]["content"].value
    new_list = invariant_map(lambda item: item["content"] == test_message_content, message_list)

    for i, new_item in enumerate(new_list):
        assert new_item.value == (message_list[i]["content"].value == test_message_content)

def test_map_maintains_addresses(message_list: list):
    # make sure the map function maintains addresses when applying a function
    new_list = invariant_map(lambda item: item, message_list)

    for i, new_item in enumerate(new_list):
        assert new_item.addresses == message_list[i].addresses

def test_reduce(invariant_number_list: list):
    # make sure the reduce function works
    sum_of_list = 0
    for item in invariant_number_list:
        sum_of_list += item.value

    reduced = invariant_reduce(lambda a, b: a + b, 0, invariant_number_list)

    assert reduced.value == sum_of_list
    assert type(reduced) == InvariantNumber

def test_reduce_raw(invariant_number_list: list):
    # make sure the reduce_raw returns the correct value and removes address information
    sum_of_list = 0
    for item in invariant_number_list:
        sum_of_list += item.value

    reduced = invariant_reduce_raw(lambda a, b: a + b, 0, invariant_number_list)

    assert reduced == sum_of_list
    assert type(reduced) == int

def test_min_helper(invariant_number_list: list):
    # make sure the min helper returns correct value and only keeps one address
    min_of_list = min([item.value for item in invariant_number_list])
    min_value = min(invariant_number_list)

    assert min_value.value == min_of_list
    assert len(min_value.addresses) == 1


def test_max_helper(invariant_number_list: list):
    # make sure the min helper returns correct value and only keeps one address
    max_of_list = max([item.value for item in invariant_number_list])

    max_value = max(invariant_number_list)

    assert max_value.value == max_of_list
    assert len(max_value.addresses) == 1

def test_sum_helper(invariant_number_list: list):
    # make sure the sum helper returns correct value and keeps all addresses
    sum_of_list = sum([item.value for item in invariant_number_list])
    sum_value = sum(invariant_number_list)

    assert type(sum_value) == InvariantNumber
    assert sum_value.value == sum_of_list
    assert len(sum_value.addresses) == len(invariant_number_list)

def test_count_helper(invariant_string_list: list):
    # make sure the count helper returns correct value and keeps all addresses
    string_to_count = '12'

    count_value = invariant_count(string_to_count, invariant_string_list)
    real_count = sum([1 if item.value == string_to_count else 0 for item in invariant_string_list])

    assert type(count_value) == InvariantNumber
    assert count_value.value == real_count
    assert len(count_value.addresses) == len(invariant_string_list)

def test_any_helper(invariant_bool_list: list):
    # make sure the any helper returns correct value and keeps all addresses
    any_value = invariant_any(invariant_bool_list)

    assert type(any_value) == InvariantBool
    assert any_value.value == True
    assert len(any_value.addresses) == len(invariant_bool_list)

def test_all_helper(invariant_bool_list: list):
    # make sure the all helper returns correct value and keeps all addresses
    all_value = invariant_all(invariant_bool_list)

    assert type(all_value) == InvariantBool
    assert all_value.value == False
    assert len(all_value.addresses) == len(invariant_bool_list)

