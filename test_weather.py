# content of tests/test_weather.py
# for pytest parametrization

from invariant_runner.testing import (
    Trace,
    expect_equals,
)


def test_soft_assert():
    # obtain some trace
    trace = Trace(
        trace=[
            {
                "role": "user",
                "content": "Could you kindly show me the list of files in tmp directory in my file system including the hidden one?",
            },
            {
                "role": "assistant",
                "content": "In the current directory, there is one file: **report.txt**. There are no hidden files listed.",
            },
        ]
    )

    with trace.as_context():
        # get the second message from the trace
        msg = trace.messages(1)

        # expect_equals compares two values
        expect_equals("assistant", msg["role"])
