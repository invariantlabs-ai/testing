"""Defines the Assertion class for test results."""

from typing import Literal

from pydantic import BaseModel


class Assertion(BaseModel):
    """Describes an assertion in a test."""

    type: Literal["SOFT", "HARD"]
    content: str
    passed: bool
