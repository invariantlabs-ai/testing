"""Contains sample tests which use the Invariant Runner."""

from invariant_runner.custom_types.assertions import (
    assert_equals,
    assert_that,
    expect_equals,
)
from invariant_runner.custom_types.matchers import HasSubstring
from invariant_runner.custom_types.trace import Trace
from invariant_runner.manager import Manager

def is_similar_to(expected: str, threshold: float = 0.8):
    pass

def test_another_agent_response():
    """Test another agent response."""
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    
    with Manager(trace):
        # assert_equals("Hello three", trace.messages()[0]["content"], "First message should greet 'three'")
        # expect_equals("Hello three", trace.messages()[0]["content"], "First message should greet 'three'")
        # expect_equals("What's Up?", trace.messages()[0]["content"], "First message should greet 'What's Up?'")
        # assert_equals("Hello three", trace.messages()[0]["content"], "First message should greet 'three'")
