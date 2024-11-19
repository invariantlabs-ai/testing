"""Describes an invariant value in a test."""

# pylint: disable=import-outside-toplevel
from typing import Any


class InvariantValue:
    """Describes an invariant value in a test."""

    def __init__(self, value: Any, addresses: list[str] = None):
        if addresses is not None and not all(
            isinstance(addr, str) for addr in addresses
        ):
            raise TypeError("addresses must be a list of strings")
        self.value = value
        self.addresses = addresses if addresses is not None else []
        if isinstance(self.value, str):
            for i, a in enumerate(self.addresses):
                if ":" not in a:
                    self.addresses[i] = a + ":0-" + str(len(self.value))

    @staticmethod
    def of(value: Any, address: list[str]):
        """Create an Invariant type object from a value and a list of addresses."""
        from .invariant_bool import InvariantBool
        from .invariant_dict import InvariantDict
        from .invariant_list import InvariantList
        from .invariant_number import InvariantNumber
        from .invariant_string import InvariantString

        if isinstance(value, list):
            assert isinstance(
                address, list
            ), "InvariantValue.of requires a list of adresses for list values"
            return InvariantList(value, address)
        elif isinstance(value, dict):
            assert isinstance(address, list), (
                "InvariantValue.of requires a list of adresses for dict values, got "
                + str(address)
                + " "
                + str(type(address))
            )
            return InvariantDict(value, address)
        elif isinstance(value, (int, float)):
            return InvariantNumber(value, address)
        elif isinstance(value, str):
            return InvariantString(value, address)
        elif isinstance(value, bool):
            return InvariantBool(value, address)
        return InvariantValue(value, address)

    def equals(self, value: Any) -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value is equal to the given value."""
        from .invariant_bool import InvariantBool

        cmp_result = self.value == value
        return InvariantBool(cmp_result, self.addresses)

    def matches(self, matcher: "Matcher") -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value matches the given matcher."""
        from .invariant_bool import InvariantBool

        cmp_result = matcher.matches(self.value)
        return InvariantBool(cmp_result, self.addresses)

    def __str__(self):
        return str(self.value) + " at " + " -> ".join(self.addresses)

    def __repr__(self):
        return str(self)
