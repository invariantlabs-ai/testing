"""InvariantDict class definition"""

from invariant.custom_types.invariant_bool import InvariantBool
from invariant.custom_types.invariant_value import InvariantValue


class InvariantDict:
    """InvariantDict class definition"""

    def __init__(self, value: dict, address: list):
        """Initialize an InvariantDict with a value and a list of addresses."""
        if not isinstance(value, dict):
            raise TypeError("value must be a dictionary, got " + str(type(value)))
        if not isinstance(address, list):
            raise TypeError("addresses must be a list, got " + str(type(address)))
        self.value = value
        self.addresses = address

    def __getitem__(self, key) -> InvariantValue | None:
        """Allows for dictionary-like access to the value using square brackets."""
        if key not in self.value:
            raise KeyError(f"Key {key} not found in {self.value}")

        value = self.value[key]
        if value is None:
            return None

        return InvariantValue.of(value, [f"{a}.{key}" for a in self.addresses])

    def get(self, key, default=None) -> InvariantValue | None:
        """Get the value of the key or return the default value if the key is not found."""
        value = self.value.get(key)
        if value is None:
            return default

        return InvariantValue.of(value, [f"{a}.{key}" for a in self.addresses])

    def __str__(self):
        return "InvariantDict" + str(self.value) + " at " + str(self.addresses)

    def matches(self, matcher: "Matcher") -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value matches the given matcher."""

        cmp_result = matcher.matches(self.value)
        return InvariantBool(cmp_result, self.addresses)

    def __repr__(self):
        return str(self)
