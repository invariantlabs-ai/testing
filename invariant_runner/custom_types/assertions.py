"""Defines the expect functions."""

from typing import Literal

from invariant_runner.custom_types.assertion_result import AssertionResult
from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_value import InvariantValue
from invariant_runner.custom_types.matchers import Matcher
from invariant_runner.manager import Manager


def assert_equals(
    expected_value: InvariantValue,
    actual_value: InvariantValue,
    message: str = None,
    assertion_type: Literal["SOFT", "HARD"] = "HARD",
):
    """Expect the invariant value to be equal to the given value."""

    ctx = Manager.current()
    comparison_result = actual_value.equals(expected_value)
    assertion = AssertionResult(
        passed=comparison_result.value,
        type=assertion_type,
        addresses=comparison_result.addresses,
        message=message,
    )
    ctx.assertions.append(assertion)


def expect_equals(
    expected_value: InvariantValue, actual_value: InvariantValue, message: str = None
):
    """Expect the invariant value to be equal to the given value. This is a soft assertion."""
    assert_equals(expected_value, actual_value, message=message, assertion_type="SOFT")


def assert_that(
    actual_value: InvariantValue,
    matcher: Matcher,
    message: str = None,
    assertion_type: Literal["SOFT", "HARD"] = "HARD",
):
    """Expect the invariant value to match the given matcher."""
    ctx = Manager.current()
    comparison_result = actual_value.matches(matcher)
    assertion = AssertionResult(
        passed=comparison_result.value,
        type=assertion_type,
        addresses=comparison_result.addresses,
        message=message,
    )
    ctx.assertions.append(assertion)


def expect_that(actual_value: InvariantValue, matcher: Matcher, message: str = None):
    """Expect the invariant value to match the given matcher. This is a soft assertion."""
    assert_that(
        actual_value,
        matcher,
        message,
        "SOFT",
    )


def assert_true(
    actual_value: InvariantBool,
    message: str = None,
    assertion_type: Literal["SOFT", "HARD"] = "HARD",
):
    """Expect the invariant value to match the given matcher."""
    ctx = Manager.current()
    comparison_result = actual_value.value
    assertion = AssertionResult(
        passed=comparison_result.value,
        type=assertion_type,
        addresses=comparison_result.addresses,
        message=message,
    )
    ctx.assertions.append(assertion)


def assert_false(
    actual_value: InvariantBool,
    message: str = None,
    assertion_type: Literal["SOFT", "HARD"] = "HARD",
):
    """Expect the invariant value to match the given matcher."""
    ctx = Manager.current()
    comparison_result = not actual_value.value
    assertion = AssertionResult(
        passed=comparison_result.value,
        type=assertion_type,
        addresses=comparison_result.addresses,
        message=message,
    )
    ctx.assertions.append(assertion)
