"""Contains sample tests which use the Invariant Runner."""

import pytest
from invariant_runner.custom_types.assertions import (
    assert_equals,
    assert_false,
    assert_that,
    assert_true,
    expect_equals,
)
from invariant_runner.custom_types.matchers import HasSubstring
from invariant_runner.custom_types.trace import Trace
from invariant_runner.manager import Manager


@pytest.fixture(name="trace_with_tool_calls")
def trace_with_tool_calls_fixture():
    """Return a trace with tool calls."""
    return Trace(
        trace=[
            {"role": "user", "content": "Hello there"},
            {
                "role": "assistant",
                "content": "Hello there",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {"name": "greet", "arguments": {"name": "there"}},
                    }
                ],
            },
            {"role": "user", "content": "I need help with something."},
            {
                "role": "assistant",
                "content": "I need help with something",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "help",
                            "arguments": {"thing": "something"},
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "ask",
                            "arguments": {"question": "what do you need help with?"},
                        },
                    },
                ],
            },
        ]
    )


def is_similar_to(expected: str, threshold: float = 0.8):
    pass


def test_another_agent_response():
    """Test another agent response."""
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])

    with Manager(trace):
        expect_equals(
            "Hello three",
            trace.messages()[0]["content"],
            "First message should greet 'three'",
        )
        expect_equals(
            "What's Up?",
            trace.messages()[0]["content"],
            "First message should greet 'What's Up?'",
        )
        assert_equals(
            "Hello three",
            trace.messages()[0]["content"],
            "First message should greet 'three'",
        )
        assert_that(
            trace.messages()[0]["content"],
            HasSubstring("hsfa"),
            "First message should match 'hsfa'",
        )


def test_trace_with_tool_calls(trace_with_tool_calls: Trace):
    """Test trace with tool calls."""
    with Manager(trace_with_tool_calls):
        tool_calls_with_greet = trace_with_tool_calls.tool_calls(
            name=lambda n: n == "greet"
        )
        assert_true(
            tool_calls_with_greet.len() == 1,
            "There should be one tool call with name 'greet'",
        )

        tool_calls_with_e = trace_with_tool_calls.tool_calls(name=lambda n: "e" in n)
        assert_true(
            tool_calls_with_e.len() < 3,
            "There should be less than two tool calls with 'e' in the name",
        )
        assert_false(
            1 > tool_calls_with_e.len(),
            "There should be less than two tool calls with 'e' in the name",
        )

        tool_calls_with_type_function = trace_with_tool_calls.tool_calls(
            type="function"
        )
        assert_true(
            tool_calls_with_type_function.len() >= 3,
            "There should be at least three tool calls with type 'function'",
        )
        assert_false(
            0 == tool_calls_with_type_function.len(),
            "There should be at least three tool calls with type 'function'",
        )
