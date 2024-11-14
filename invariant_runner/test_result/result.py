"""Decribes the result class for the invariant runner."""

from pydantic import BaseModel

from invariant_runner.test_result.assertion import Assertion


class TestResult(BaseModel):
    """Result of a test run."""

    name: str
    trace: list[dict]
    passed: bool
    assertions: list[Assertion]
