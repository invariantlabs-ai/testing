"""Describes an invariant value in a test."""

from typing import Any


class InvariantValue:
    """Describes an invariant value in a test."""

    def __init__(self, value: Any, addresses: list[str] = []):
        self.value = value
        self.addresses = addresses

    def equals(self, value: Any):
        """Check if the value is equal to the given value."""
        cmp_result = self.value == value
        return InvariantValue(cmp_result, self.addresses)

    def __str__(self):
        return str(self.value) + " at " + " -> ".join(self.addresses)

    def __repr__(self):
        return str(self)
