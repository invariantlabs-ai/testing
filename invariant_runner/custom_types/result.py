"""Decribes the result class for the invariant runner."""

from pydantic import BaseModel

from invariant_runner.custom_types.assertion import Assertion
from invariant_runner.custom_types.trace import Trace


class TestResult(BaseModel):
    """Result of a test run."""

    name: str
    trace: Trace
    passed: bool
    assertions: list[Assertion]
