"""Defines the expect functions."""

from typing import Literal

from invariant_runner.custom_types.assertion import Assertion
from invariant_runner.custom_types.invariant_value import InvariantValue
from invariant_runner.manager import Manager


def assert_equals(
    expected_value: InvariantValue,
    actual_value: InvariantValue,
    assertion_type: Literal["SOFT", "HARD"] = "HARD",
):
    """Expect the invariant value to be equal to the given value."""
    ctx = Manager.current()
    comparison_result = actual_value.equals(expected_value)
    assertion = Assertion(
        passed=comparison_result.value,
        type=assertion_type,
        addresses=comparison_result.addresses,
    )
    ctx.assertions.append(assertion)


def expect_equals(expected_value: InvariantValue, actual_value: InvariantValue):
    """Expect the invariant value to be equal to the given value. This is a soft assertion."""
    assert_equals(expected_value, actual_value, "SOFT")
