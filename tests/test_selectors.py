"""Tests for the invariant_runner module."""

import pytest
from invariant_runner.custom_types.trace import Trace


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

@pytest.fixture
def trace_with_tool_calls():
    return Trace(trace=[
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "Hello there", "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "greet",
                    "arguments": {
                        "name": "there"
                    }
                }
            }
        ]},
        {"role": "user", "content": "I need help with something."},
        {"role": "assistant", "content": "I need help with something", "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "help",
                    "arguments": {
                        "thing": "something"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ask",
                    "arguments": {
                        "question": "what do you need help with?"
                    }
                }
            }
        ]}
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

def test_messages_filter_callable_user_with_string_upper(trace: Trace):
    assert trace.messages(role=lambda r: r == "user")[0]["content"].upper() == "HELLO THERE"

def test_messages_filter_callable_user_with_string_lower(trace: Trace):
    assert trace.messages(role=lambda r: r == "user")[0]["content"].lower() == "hello there"

def test_messages_filter_callable_multiple(trace: Trace):
    assert trace.messages(role=lambda r: r == "user", content=lambda c: "computer" in c)[0]["content"].value == "I need help with my computer."

def test_messages_filter_callable_multiple_2(trace: Trace):
    assert trace.messages(role="user", content=lambda c: "computer" in c)[0]["content"].value == "I need help with my computer."

def test_tool_calls(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls()
    assert tool_calls.len().value == 3

def test_tool_calls_filter(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls(type="function")
    assert tool_calls.len().value == 3

def test_tool_calls_filter_callable(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls(function=lambda f: f["name"] == "greet")
    assert tool_calls.len().value == 1

def test_tool_calls_filter_name(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls(name="greet")
    assert tool_calls.len().value == 1

def test_tool_calls_filter_name_callable(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls(name=lambda n: n == "greet")
    assert tool_calls.len().value == 1

def test_tool_calls_filter_name_callable_2(trace_with_tool_calls: Trace):
    tool_calls = trace_with_tool_calls.tool_calls(name=lambda n: "e" in n)
    assert tool_calls.len().value == 2