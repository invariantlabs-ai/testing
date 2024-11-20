"""Contains sample tests which use the Invariant Runner."""

import pytest

from invariant_runner.custom_types.assertions import (
    assert_equals,
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
            trace.messages()[0]["content"].len(),
            "First message should greet 'three'",
        )
        assert_that(
            trace.messages()[0]["content"],
            HasSubstring("hsfa"),
            "First message should match 'hsfa'",
        )


@pytest.fixture
def big_trace():
    return Trace(
        trace=[
            {
                "role": "user",
                "content": "Could you kindly show me the list of files in tmp directory in my file system including the hidden one?",
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_ls7AnBVJzZQPHTrKg0G7",
                        "type": "function",
                        "function": {"name": "cd", "arguments": {"folder": "tmp"}},
                    }
                ],
            },
            {
                "role": "tool",
                "content": '{"error": "cd: tmp: No such directory. You cannot use path to change directory."}',
                "tool_call_id": "call_ls7AnBVJzZQPHTrKg0G7",
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_6DKFVzXQkTT0fTUDy7lw",
                        "type": "function",
                        "function": {"name": "ls", "arguments": {"a": True}},
                    }
                ],
            },
            {
                "role": "tool",
                "content": '{"current_directory_content": ["report.txt"]}',
                "tool_call_id": "call_6DKFVzXQkTT0fTUDy7lw",
            },
            {
                "role": "assistant",
                "content": "In the current directory, there is one file: **report.txt**. There are no hidden files listed.",
            },
            {
                "role": "user",
                "content": "There is a report in my current directory. I have noticed the report appears somewhat cluttered; it could benefit from having its lines sorted.",
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_QxxWLVviOvv7XXrXLxoN",
                        "type": "function",
                        "function": {
                            "name": "sort",
                            "arguments": {"file_name": "report.txt"},
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "content": '{"sorted_content": "Initial report content Unsorted data More unsorted data"}',
                "tool_call_id": "call_QxxWLVviOvv7XXrXLxoN",
            },
            {
                "role": "assistant",
                "content": "The lines in **report.txt** have been sorted. The sorted content is as follows:\n\n```\nInitial report content\nMore unsorted data\nUnsorted data\n``` \n\nIf you need any further modifications or actions, feel free to ask!",
            },
            {
                "role": "user",
                "content": "I would appreciate it if you could share the sorted result as the message body on social media, ensuring to tag 'currenttechtrend' and mention Julia, our insightful team.",
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_heZY5J5gObsexwC6CTcu",
                        "type": "function",
                        "function": {
                            "name": "post_tweet",
                            "arguments": {
                                "content": "Initial report content\nMore unsorted data\nUnsorted data",
                                "tags": [],
                                "mentions": ["@currenttechtrend", "@Julia"],
                            },
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "content": '{"id": 2, "username": "tech_guru", "content": "Initial report content\\nMore unsorted data\\nUnsorted data", "tags": [], "mentions": ["@currenttechtrend", "@Julia"]}',
                "tool_call_id": "call_heZY5J5gObsexwC6CTcu",
            },
            {
                "role": "assistant",
                "content": "The sorted report has been successfully posted on social media. Here are the details:\n\n- **Content:** \n  ```\n  Initial report content\n  More unsorted data\n  Unsorted data\n  ```\n- **Mentions:** @currenttechtrend, @Julia\n\nIf there's anything else you need, just let me know!",
            },
        ]
    )


def test_big_trace(big_trace):
    """Test trace with tool calls."""
    with Manager(big_trace):
        for tc in big_trace.messages(role="assistant"):
            assert_true(
                tc["content"].len() == 0
                or tc["content"].contains("current")
                or tc["content"].contains("lines"),
                "Assistant message content should be empty",
            )

            assert_equals(
                "", tc["content"], "Assistant message content should be empty"
            )


def test_trace_rules(trace_with_tool_calls: Trace):
    """Test trace rules."""
    with Manager(trace_with_tool_calls):
        tool_calls_with_greet = trace_with_tool_calls.tool_calls(name=lambda n: n == "greet")
        assert_true(tool_calls_with_greet[0]["function"]["name"] == "greet")

        tool_calls_with_ask = trace_with_tool_calls.tool_calls(name=lambda n: n == "ask")
        assert_true(tool_calls_with_ask[0]["function"]["arguments"]["question"].contains("help"))
        assert_true(not tool_calls_with_ask[0]["function"]["arguments"]["question"].contains("helpp"))

        assistant_messages = trace_with_tool_calls.messages(role="assistant")
        assert assistant_messages.len() == 2
        assert_equals("Hello there", assistant_messages[0]["content"], "First message should greet 'there'")
        assert_equals("I need help with something", assistant_messages[1]["content"], "Second message should greet 'something'")

        
