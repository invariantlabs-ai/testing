"""Contains sample tests which use the Invariant Runner."""

from invariant_runner.custom_types.assertions import (
    assert_equals,
    assert_that,
    expect_equals,
)
from invariant_runner.custom_types.matchers import HasSubstring
from invariant_runner.custom_types.trace import Trace
from invariant_runner.manager import Manager


def test_another_agent_response():
    """Test another agent response."""
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    with Manager(trace) as _:
        assert_equals("Hello three", trace.messages()[0]["content"])
        expect_equals("Hello there", trace.messages()[0]["content"])
        assert_that(trace.messages()[0]["content"], HasSubstring("the"))
