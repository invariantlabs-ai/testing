"""Decribes the result class for the invariant runner."""

from invariant_runner.custom_types.assertion_result import AssertionResult
from invariant_runner.custom_types.trace import Trace
from pydantic import BaseModel


class TestResult(BaseModel):
    """Result of a test run."""

    name: str
    trace: Trace
    passed: bool
    assertions: list[AssertionResult]
    explorer_url: str
