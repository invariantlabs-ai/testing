import invariant.testing.functional as F
from invariant.testing import Trace, assert_equals, assert_true, expect_equals

from .testutils import should_fail_with


@should_fail_with(num_assertion=1)
def test_in():
    """Test that expect_equals works fine with the right order."""
    trace = Trace(
        trace=[
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "there where!?"},
            {"role": "assistant", "content": "Hello to you as well"},
        ]
    )

    with trace.as_context():
        assert_true(F.len(trace.messages(content=lambda c: "Hello" in c)) == 3)
        assert_true(F.len(trace.messages(content=lambda c: "there" in c)) == 2)


@should_fail_with(num_assertion=1)
def test_in2():
    """Test that expect_equals works fine with the right order."""
    trace = Trace(
        trace=[
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "there where!?"},
            {"role": "assistant", "content": "Hello to you as well"},
        ]
    )

    with trace.as_context():
        trace.messages(content=lambda c: "Hello" in c)
        assert_true(
            F.len(
                F.filter(
                    lambda x: x,
                    F.map(lambda c: c["content"].contains("Hello"), trace.messages()),
                )
            )
            == 3
        )
        assert_true(
            F.len(
                F.filter(
                    lambda x: x,
                    F.map(lambda c: c["content"].contains("there"), trace.messages()),
                )
            )
            == 2
        )
