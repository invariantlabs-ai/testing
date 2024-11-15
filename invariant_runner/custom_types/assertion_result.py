"""Defines the Assertion class for test results."""

from typing import List, Literal

from pydantic import BaseModel


class AssertionResult(BaseModel):
    """Describes an assertion in a test."""

    passed: bool
    type: Literal["SOFT", "HARD"]
    addresses: List[str]
