"""Tests for the invariant_runner module."""

from invariant_runner.custom_types.trace import Trace
import pytest

@pytest.fixture
def trace():
    return Trace(trace=[
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

def test_messages_list_select(trace: Trace):
    assert trace.messages()[1]["content"].value == trace.trace[1]["content"]

def tests_messages_index_select(trace: Trace):
    assert trace.messages(1)["content"].value == trace.trace[1]["content"]

def test_messages_filter(trace: Trace):
    assert trace.messages(role="assistant")[0]["content"].value == "Hi, how can I help you?"

def test_messages_filter_callable(trace: Trace):
    assert trace.messages(role=lambda r: r == "assistant")[0]["content"].value == "Hi, how can I help you?"

def test_messages_filter_callable_user(trace: Trace):
    assert trace.messages(role=lambda r: r == "user")[0]["content"].value == "Hello there"

def test_messages_filter_callable_multiple(trace: Trace):
    assert trace.messages(role=lambda r: r == "user", content=lambda c: "computer" in c)[0]["content"].value == "I need help with my computer."

def test_messages_filter_callable_multiple_2(trace: Trace):
    assert trace.messages(role="user", content=lambda c: "computer" in c)[0]["content"].value == "I need help with my computer."