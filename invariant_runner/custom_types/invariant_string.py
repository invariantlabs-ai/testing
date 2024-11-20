"""Describes an invariant string in a test."""

from typing import Union

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantString(InvariantValue):
    """Describes an invariant string in a test."""

    def __init__(self, value: str, addresses: list[str] = None):
        if not isinstance(value, str):
            raise TypeError(f"value must be a str, got {type(value)}")
        if addresses is None:
            addresses = []
        super().__init__(value, addresses)

    def __eq__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is equal to the given string."""
        if isinstance(other, InvariantString):
            other = other.value
        return InvariantBool(self.value == other, self.addresses)

    def __ne__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is not equal to the given string."""
        if isinstance(other, InvariantString):
            other = other.value
        return InvariantBool(self.value != other, self.addresses)

    def contains(self, substring: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string contains the given substring."""
        if isinstance(substring, InvariantString):
            substring = substring.value
        return InvariantBool(substring in self.value, self.addresses)

    def __add__(self, other: Union[str, "InvariantString"]) -> "InvariantString":
        """Concatenate the string with another string."""
        if isinstance(other, InvariantString):
            return InvariantString(
                self.value + other.value, self.addresses + other.addresses
            )
        return InvariantString(self.value + other, self.addresses)

    def __radd__(self, other: str) -> "InvariantString":
        """Concatenate another string with this string (reverse operation)."""
        return InvariantString(other + self.value, self.addresses)

    def __str__(self) -> str:
        return f"InvariantString(value={self.value}, addresses={self.addresses})"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self):
        raise NotImplementedError(
            "InvariantList does not support len(). Please use .len() instead."
        )

    def len(self):
        """Return the length of the list."""
        from invariant_runner.custom_types.invariant_number import InvariantNumber

        return InvariantNumber(len(self.value), self.addresses)
