---
title: Tests
---

# Writing Tests

<div class='subtitle'>Writing agent tests</div>

`testing` allows you to write tests for your AI agent just you write software unit tests. However, to make debugging and error localization easier, `testing` provides a few additional features that are not available in regular unit testing frameworks.

This chapter first discusses how _localized assertions_ work and then provides examples of how to write tests using `testing`, including _soft and hard assertions_.

## Trace Context and Localized Assertions

A test case in `testing` looks a lot like a regular unit test, except that it always makes use of a `Trace` object and the corresponding `.as_context()` method. This is required to enable _localized assertions_, that maps assertions to specific ranges in the provided trace:

```python
from invariant_runner.testing import assert_true, Trace

def test_assert():
    # obtain some trace
    trace = Trace(
        trace=[
            {"role": "user", "content": "Could you kindly show me the list of files in tmp directory in my file system including the hidden one?"},
            {"role": "assistant", "content": "In the current directory, there is one file: **report.txt**. There are no hidden files listed."},
        ]
    )

    # run the test in the context of the trace
    with trace.as_context():
        
        # get the second message from the trace
        msg = trace.messages(1)

        # a hard assertion on the message content
        assert_true(
            msg["content"].contains("current"),
            "Assistant message content should contain the word 'current'",
        )
```

With this basic setup, you can now write tests for your agent.

## `assert_true` and `assert_that` and `assert_equals`

To make hard (leading to test failure) assertions, you can use the `assert_true`, `assert_that`, and `assert_equals` functions. These functions are similar to the ones you might know from unit testing frameworks like `unittest` or `pytest`, but they add support for localization.

```python
from invariant_runner.testing import assert_true, assert_equals, assert_that, Trace, IsSimilar

def test_hard_assert():
    # obtain some trace
    trace = Trace(
        trace=[
            {"role": "user", "content": "Could you kindly show me the list of files in tmp directory in my file system including the hidden one?"},
            {"role": "assistant", "content": "In the current directory, there is one file: **report.txt**. There are no hidden files listed."},
        ]
    )

    with trace.as_context():
        # get the second message from the trace
        msg = trace.messages(1)

        # assert_equals compares two values
        assert_equals("assistant", msg["role"])

        # assert_true checks for a boolean condition
        assert_true(
            msg["content"].contains("current"),
            "Assistant message content should contain the word 'current'",
        )

        # assert_that uses a fuzzy matcher to check the message content
        assert_that(msg["content"], IsSimilar("current directory one file: **report.txt**. There are no hidden files listed.", threshold=0.8), "Message content should be similar")
```

This snippet demonstrates three types of hard assertions:


### `assert_equals`
```py
def assert_equals(
    expected_value: InvariantValue,
    actual_value: InvariantValue,
    message: str = None
)
```

- `assert_equals` compares two values for equality (same string, number, etc.).


### `assert_true`
```py
def assert_true(
    actual_value: InvariantBool | bool,
    message: str = None
)
```

- `assert_true` checks for a boolean condition (true or false), e.g. the result of a `.contains(...)` check.


### `assert_that`
```py
def assert_that(
    actual_value: InvariantValue,
    matcher: Matcher,
    message: str = None
)
```

- `assert_that` uses a designated `Matcher` class to check the message content. In this case, `IsSimilar` is used to compare the message content to some expected value with a given threshold for maximum allowed difference.