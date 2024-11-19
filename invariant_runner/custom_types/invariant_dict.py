"""InvariantDict class definition"""

from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantDict:
    """InvariantDict class definition"""

    def __init__(self, value, address):
        self.value = value
        self.address = address

    def __getitem__(self, key):
        return InvariantValue(self.value[key], [f"{self.address}.{key}"])

    def __str__(self):
        return str(self.value) + " at " + str(self.address)

    def __repr__(self):
        return str(self)
