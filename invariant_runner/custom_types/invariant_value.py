"""Describes an invariant value in a test."""

from typing import Any


class InvariantValue:
    """Describes an invariant value in a test."""

    def __init__(self, value: Any, addresses: list[str] = []):
        self.value = value
        self.addresses = addresses

        assert self.addresses is not None, "InvariantValue must have addresses"

        if type(self.value) is str:
            for i,a in enumerate(self.addresses):
                if not ":" in a:
                    self.addresses[i] = a + ":0-" + str(len(self.value))

    @staticmethod
    def of(value: Any, address: list[str]):
        from .invariant_list import InvariantList
        from .invariant_dict import InvariantDict

        if type(value) is list:
            assert type(address) is list, "InvariantValue.of requires a list of adresses for list values"
            return InvariantList(value, address)
        elif type(value) is dict:
            assert type(address) is list, "InvariantValue.of requires a list of adresses for dict values, got " + str(address) + " " + str(type(address))
            return InvariantDict(value, address)
        return InvariantValue(value, address)

    def equals(self, value: Any) -> "InvariantValue":
        """Check if the value is equal to the given value."""
        cmp_result = self.value == value
        return InvariantValue(cmp_result, self.addresses)

    def matches(self, matcher: "Matcher") -> "InvariantValue":
        """Check if the value matches the given matcher."""
        cmp_result = matcher.matches(self.value)
        return InvariantValue(cmp_result, self.addresses)

    def __str__(self):
        return str(self.value) + " at " + " -> ".join(self.addresses)

    def __repr__(self):
        return str(self)