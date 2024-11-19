"""InvariantDict class definition"""

from invariant_runner.custom_types.invariant_value import InvariantValue

class InvariantList:
    """InvariantList class definition"""

    def __init__(self, values, addresses: list[list[str]]):
        self.value = values
        self.addresses = addresses

    @classmethod
    def from_values(cls, values: list[InvariantValue]):
        return cls([value.value for value in values], [value.address for value in values])

    def __getitem__(self, key: int):
        return InvariantValue.of(self.value[key], self.addresses[key])

    def __len__(self):
        raise NotImplementedError("InvariantList does not support len(). Please use .len() instead.")
    
    def len(self) -> InvariantValue:
        return InvariantValue.of(len(self.value), self.addresses)
    
    def __iter__(self):
        for i in range(len(self.value)):
            yield self[i]

    def __contains__(self, value):
        # assumes proper equality checking
        return any(value == item for item in self.value)

    def __str__(self):
        return "InvariantList" + str(self.value) + " at " + str(self.addresses)

    def __repr__(self):
        return str(self)
