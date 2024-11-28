---
title: Quickstart
---

# Getting Started with Invariant Testing

<div class='subtitle'>Build your first agent test case and run it.</div>

This quickstart guide demonstrates how to write and run your first agent test case.

## 1. Install the Testing library

First, install the Invariant Testing library using pip:

```bash
pip install invariant
```

## 2. Create a test case

To get started, first create a `tests/` folder in your project root. This folder will contain all your test files.

Next, create a new file in `tests/` and name it `test_example.py` as shown below:

```python
from invariant.testing import Trace, assert_true

def test_weather():
    # create a Trace object from your agent trajectory
    trace = Trace(trace=[
        {"role": "user", "content": "What is the weather like in Paris?"},
        {"role": "agent", "content": "The weather in London is 75°F and sunny."},
    ])

    # make assertions about the agent's behavior
    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains("Paris"),
            "The agent should respond about Paris",
        )
```

This file defines a single test case, `test_weather`, which tests the agent's response to a user query about the weather in Paris. In its assertions, the test checks that the agent provides weather information about Paris.


## 2. Run your Test Case

To run your test case, you can use `invariant test` in your project root.

```bash
invariant test
```

Given the test case above, this test will actually fail since the agent trace does not contain a response about Paris. Thus, the output will look like this:

```py
__________________________________________ test_weather __________________________________________
ERROR: 1 hard assertions failed:

 
        {"role": "user", "content": "What is the weather like in Paris?"},
        {"role": "agent", "content": "The weather in London is 75°F and sunny."},
    ])

    with trace.as_context():
>       assert_true(
            trace.messages()[-1]["content"].contains("Paris"),
            "The agent should respond about Paris",
        )
________________________________________________________________________________

ASSERTION FAILED: The agent should respond about Paris
________________________________________________________________________________

#       role:  "user"
#       content:  "What is the weather like in Paris?"
#     },
#     {
#       role:  "agent"
        content:   "The weather in London is 75°F and sunny."
#     },
#  ]
```

As shown here, the test result will not only provide information about which assertion failed but also show the agent's trace leading up to the failure.

**Assertion Tracking** This is possible because the `Trace` object tracks all property accesses and method calls made during assertions. Because of this, failing tests can always be traced back to the relevant part of the agent's behavior, facilitating debugging and error resolution.
