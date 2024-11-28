"""Tests for the capital_finder_agent"""

import pytest
from invariant.testing import Trace, assert_equals, assert_true
from swarm import Swarm

from .capital_finder_agent import create_agent


@pytest.fixture(name="swarm_client")
def fixture_swarm_client():
    """Create a swarm client."""
    return Swarm()


def test_capital_finder_agent_when_capital_found(swarm_client):
    """Test the capital finder agent when the capital is found."""
    agent = create_agent()
    history = [{"role": "user", "content": "What is the capital of France?"}]
    response = swarm_client.run(
        agent=agent,
        messages=history,
    )
    trace = Trace.from_swarm(response, history)

    with trace.as_context():
        get_capital_tool_calls = trace.tool_calls(name=lambda n: n == "get_capital")
        assert_true(len(get_capital_tool_calls) == 1)
        assert_equals(
            "France", get_capital_tool_calls[0]["function"]["arguments"]["country_name"]
        )

        assert_true("Paris" in trace.messages(-1)["content"])


def test_capital_finder_agent_when_capital_not_found(swarm_client):
    """Test the capital finder agent when the capital is found."""
    agent = create_agent()
    history = [{"role": "user", "content": "What is the capital of Spain?"}]
    response = swarm_client.run(
        agent=agent,
        messages=history,
    )
    trace = Trace.from_swarm(response, history)

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
