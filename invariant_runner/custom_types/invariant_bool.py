"""Describes an invariant boolean in a test."""

from typing import Union

from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantBool(InvariantValue):
    """Describes an invariant bool in a test."""

    def __init__(self, value: bool, addresses: list[str] = None):
        if not isinstance(value, bool):
            raise TypeError(f"value must be a bool, got {type(value)}")
        if addresses is None:
            addresses = []
        super().__init__(value, addresses)

    def __eq__(self, other: Union[bool, "InvariantBool"]) -> "InvariantBool":
        """Check if the boolean is equal to the given boolean."""
        if isinstance(other, InvariantBool):
            other = other.value
        return InvariantBool(self.value == other, self.addresses)

    def __ne__(self, other: Union[bool, "InvariantBool"]) -> "InvariantBool":
        """Check if the boolean is not equal to the given boolean."""
        if isinstance(other, InvariantBool):
            other = other.value
        return InvariantBool(self.value != other, self.addresses)

    def __and__(self, other: Union[bool, "InvariantBool"]) -> "InvariantBool":
        """Evaluate the boolean AND with the given boolean."""
        if isinstance(other, InvariantBool):
            other = other.value
        return InvariantBool(self.value and other, self.addresses)

    def __rand__(self, other: bool) -> "InvariantBool":
        """Evaluate the boolean AND with the given boolean (reverse operation)."""
        return InvariantBool(other and self.value, self.addresses)

    def __or__(self, other: Union[bool, "InvariantBool"]) -> "InvariantBool":
        """Evaluate the boolean OR with the given boolean."""
        if isinstance(other, InvariantBool):
            other = other.value
        return InvariantBool(self.value or other, self.addresses)

    def __ror__(self, other: bool) -> "InvariantBool":
        """Evaluate the boolean OR with the given boolean (reverse operation)."""
        return InvariantBool(other or self.value, self.addresses)

    def __invert__(self) -> "InvariantBool":
        """Evaluate the boolean NOT value."""
        return InvariantBool(not self.value, self.addresses)

    def __str__(self) -> str:
        return f"InvariantBool(value={self.value}, addresses={self.addresses})"

    def __repr__(self) -> str:
        return str(self)
