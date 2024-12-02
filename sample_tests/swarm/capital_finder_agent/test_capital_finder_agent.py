"""Tests for the capital_finder_agent"""

import pytest
from invariant.testing import SwarmWrapper, assert_equals, assert_true, traced
from swarm import Swarm

from .capital_finder_agent import create_agent


@pytest.fixture(name="swarm_wrapper", scope="module")
def fixture_swarm_wrapper():
    """Create a wrapper swarm client."""
    return SwarmWrapper(Swarm())


@traced
def test_capital_finder_agent_when_capital_found(swarm_wrapper):
    """Test the capital finder agent when the capital is found."""
    agent = create_agent()
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    _ = swarm_wrapper.run(
        agent=agent,
        messages=messages,
    )
    trace = swarm_wrapper.to_invariant_trace()

    with trace.as_context():
        get_capital_tool_calls = trace.tool_calls(name=lambda n: n == "get_capital")
        assert_true(len(get_capital_tool_calls) == 1)
        assert_equals(
            "France", get_capital_tool_calls[0]["function"]["arguments"]["country_name"]
        )

        assert_true("Paris" in trace.messages(-1)["content"])


@traced
def test_capital_finder_agent_when_capital_not_found(swarm_wrapper):
    """Test the capital finder agent when the capital is found."""
    agent = create_agent()
    messages = [{"role": "user", "content": "What is the capital of Spain?"}]
    _ = swarm_wrapper.run(
        agent=agent,
        messages=messages,
    )
    trace = swarm_wrapper.to_invariant_trace()

    with trace.as_context():
        get_capital_tool_calls = trace.tool_calls(name=lambda n: n == "get_capital")
        assert_true(len(get_capital_tool_calls) == 1)
        assert_equals(
            "Spain", get_capital_tool_calls[0]["function"]["arguments"]["country_name"]
        )

        messages_with_role_tool = trace.messages(role="tool")
        assert_true(len(messages_with_role_tool) == 1)
        assert_true("not_found" in messages_with_role_tool[0]["content"])

        assert_true("Madrid" not in trace.messages(-1)["content"])
