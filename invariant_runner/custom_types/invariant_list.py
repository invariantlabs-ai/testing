"""InvariantDict class definition"""

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
