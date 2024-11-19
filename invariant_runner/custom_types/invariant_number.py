"""Describes an invariant number in a test."""

from operator import eq, ge, gt, le, lt, ne
from typing import Union

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantNumber(InvariantValue):
    """Describes an invariant number in a test."""

    def __init__(self, value: int | float, addresses: list[str] = None):
        if not isinstance(value, (int, float)):
            raise TypeError(f"value must be an int or float, got {type(value)}")
        # Move this to InvariantValue.__init__ when refactoring.
        if addresses is not None and not all(
            isinstance(addr, str) for addr in addresses
        ):
            raise TypeError("addresses must be a list of strings")
        if addresses is None:
            addresses = []
        super().__init__(value, addresses)

    def _compare(
        self, other: Union[int, float, "InvariantNumber"], operator
    ) -> "InvariantBool":
        """Helper function to compare with another number."""
        if isinstance(other, InvariantNumber):
            other = other.value
        cmp_result = operator(self.value, other)
        return InvariantBool(cmp_result, self.addresses)

    def __eq__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is equal to the given number."""
        return self._compare(other, eq)

    def __ne__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is not equal to the given number."""
        return self._compare(other, ne)

    def __gt__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is greater than the given number."""
        return self._compare(other, gt)

    def __lt__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is less than the given number."""
        return self._compare(other, lt)

    def __ge__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is greater than or equal to the given number."""
        return self._compare(other, ge)

    def __le__(self, other: Union[int, float, "InvariantNumber"]) -> "InvariantBool":
        """Check if the number is less than or equal to the given number."""
        return self._compare(other, le)

    def __str__(self) -> str:
        return f"InvariantNumber(value={self.value}, addresses={self.addresses})"

    def __repr__(self) -> str:
        return str(self)
