"""Defines the expect functions."""

from typing import Any


class Matcher:
    """Base class for all matchers."""

    def matches(self, actual_value: Any) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")


class HasSubstring(Matcher):
    """Matcher for checking if a string contains a substring."""

    def __init__(self, substring: str):
        self.substring = substring

    def matches(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, str):
            raise TypeError("HasSubstring matcher only works with strings.")
        return self.substring in actual_value

    def __str__(self):
        return f"HasSubstring({self.substring})"

    def __repr__(self):
        return str(self)