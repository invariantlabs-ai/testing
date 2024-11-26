"""Tests for the invariant_runner module."""

import pytest
from invariant_runner.custom_types.invariant_list import InvariantList
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

def test_list_index_access(message_list: InvariantList):
    assert message_list[1]["content"].value == "Hi, how can I help you?"

def test_list_length(message_list: InvariantList):
    # make sure len(...) fails
    with pytest.raises(NotImplementedError):
        print(len(message_list))

def test_list_length_with_member(message_list: InvariantList):
    # make sure len(...) fails
    assert message_list.len().value == 9

def test_list_iteration(message_list: InvariantList):
    for i, message in enumerate(message_list):
        assert message["content"].value == message_list[i]["content"].value