"""InvariantDict class definition"""
from typing import Callable, Any, Union

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantList:
    """InvariantList class definition"""

    def __init__(self, values, addresses: list[list[str]]):
        self.value = values
        self.addresses = addresses

    def __eq__(self, other: "InvariantList") -> bool:
        if not isinstance(other, InvariantList):
            raise TypeError(
                "Cannot compare InvariantList with non-InvariantList")
        return self.value == other.value and self.addresses == other.addresses

    @classmethod
    def from_values(cls, values: list[InvariantValue]):
        """Create an InvariantList from a list of InvariantValues."""
        return cls(
            [value.value for value in values], [
                value.addresses for value in values]
        )

    def __getitem__(self, key: int):
        return InvariantValue.of(self.value[key], self.addresses[key])

    def __len__(self):
        raise NotImplementedError(
            "InvariantList does not support len(). Please use .len() instead."
        )

    def len(self) -> InvariantNumber:
        """Return the length of the list."""
        # flatten addresses
        return InvariantNumber(
            len(self.value), [
                item for sublist in self.addresses for item in sublist]
        )

    def __iter__(self):
        for i in range(len(self.value)):
            yield self[i]

    def __contains__(self, value):
        # assumes proper equality checking
        return any(value == item for item in self.value)

    def __str__(self):
        # if each element is a dict, print each dict on a new line
        if any(isinstance(item, dict) for item in self.value):
            return (
                "InvariantList[\n"
                + "\n".join("  " + str(item) for item in self.value)
                + "\n]"
                + " at " + str(self.addresses)
            )
        return "InvariantList" + str(self.value) + " at " + str(self.addresses)

    def __repr__(self):
        return str(self)

    def map(self, func: Callable[[InvariantValue], InvariantValue]) -> "InvariantList":
        """Apply a function to each element in the list."""
        return InvariantList(
            [func(item) for item in self.__iter__()], self.addresses
        )

    def reduce_raw(self, func: Callable[[Any, Any], Any], initial_value: Any) -> Any:
        """
        Reduce the list instance to a single value using a function and disregarding address information.
        Use this method instead of 'reduce' when the 'func' is not compatible with 'InvariantValue'.
        """
        # Strip address information from values
        values_ = [item.value for item in self.value]

        accumulator = initial_value
        for item in values_:
            accumulator = func(accumulator, item)
        return accumulator

    def reduce(
        self,
        func: Callable[[InvariantValue, InvariantValue], InvariantValue],
        initial_value: Union[InvariantValue, Any],
    ) -> InvariantValue:
        """Reduce the list instance to a single value using a function."""
        accumulator = initial_value
        for item in self.__iter__():
            try:
                accumulator = func(accumulator, item)
            except TypeError as e:
                raise TypeError(
                    f"Incompatible function: {func} for types '{type(accumulator).__name__}' and '{type(item).__name__}'. "
                    "Did you mean to use '.reduce_raw()'?"
                ) from e

        return accumulator

    def min(self) -> InvariantValue:
        """Return the minimum value in the list."""
        return min(self.value)

    def max(self) -> InvariantValue:
        """Return the maximum value in the list."""
        return max(self.value)

    def sum(self) -> InvariantNumber:
        """Return the sum of all values in the list."""
        return self.reduce(lambda element1, element2: element1 + element2, InvariantNumber(0, []))

    def count(self, value: Union[InvariantValue, Any]) -> InvariantNumber:
        """Return the number of occurrences of a value in the list."""
        return self.map(
            lambda a: InvariantNumber(1, a.addresses)
            if a == value
            else InvariantNumber(0, a.addresses)
        ).sum()

    def any(self) -> InvariantBool:
        """Return True if any element in the list is True."""
        return self.reduce(lambda element1, element2: element1 | element2, InvariantBool(False, []))

    def all(self) -> InvariantBool:
        """Return True if all elements in the list are True."""
        return self.reduce(lambda element1, element2: element1 & element2, InvariantBool(True, []))
