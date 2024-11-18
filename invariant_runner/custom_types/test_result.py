"""Decribes the result class for the invariant runner."""

from invariant_runner.custom_types.assertion_result import AssertionResult
from pydantic import BaseModel

from invariant_runner.custom_types.trace import Trace


class TestResult(BaseModel):
    """Result of a test run."""

    name: str
    trace: Trace
    passed: bool
    assertions: list[AssertionResult]
