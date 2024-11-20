"""InvariantDict class definition"""

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_value import InvariantValue


class InvariantDict:
    """InvariantDict class definition"""

    def __init__(self, value, address):
        self.value = value
        self.addresses = address

    def __getitem__(self, key):
        return InvariantValue.of(
            self.value[key], [f"{a}.{key}" for a in self.addresses]
        )

    def __str__(self):
        return str(self.value) + " at " + str(self.addresses)

    def matches(self, matcher: "Matcher") -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value matches the given matcher."""

        cmp_result = matcher.matches(self.value)
        return InvariantBool(cmp_result, self.addresses)

    def __repr__(self):
        return str(self)
