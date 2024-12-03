"""Helper functions for searching around collections that contain invariant values."""

# Import built-in functions to avoid shadowing
from builtins import max as builtin_max
from builtins import min as builtin_min
from collections.abc import Iterable
from typing import Any, Callable

from invariant.custom_types.invariant_bool import InvariantBool
from invariant.custom_types.invariant_number import InvariantNumber
from invariant.custom_types.invariant_value import InvariantValue

# Import built-in functions to avoid shadowing
from builtins import max as builtin_max
from builtins import min as builtin_min
from builtins import len as builtin_len


def map(  # pylint: disable=redefined-builtin
    func: Callable[[InvariantValue], InvariantValue], iterable: Iterable[InvariantValue]
) -> list[InvariantValue]:
    """Apply a function to each element in the iterable and create a new list."""
    return [func(item) for item in iterable]


def reduce_raw(
    func: Callable[[Any, Any], Any],
    initial_value: Any,
    iterable: Iterable[InvariantValue],
) -> Any:
    """Reduce the list instance to a single value using a function and disregarding address
    information.

    Use this method instead of 'reduce' when the 'func' is not compatible with 'InvariantValue'.
    """
    # Strip address information from values
    values_ = [item.value for item in iterable]

    accumulator = initial_value
    for item in values_:
        accumulator = func(accumulator, item)
    return accumulator


def reduce(
    func: Callable[[InvariantValue, InvariantValue], InvariantValue],
    initial_value: InvariantValue | Any,
    iterable: Iterable[InvariantValue],
) -> InvariantValue:
    """Reduce the list instance to a single value using a function."""
    accumulator = initial_value
    for item in iterable:
        try:
            accumulator = func(accumulator, item)
        except TypeError as e:
            raise TypeError(
                f"Incompatible function: {func} for types '{type(accumulator).__name__}' \
                and '{type(item).__name__}'. "
                "Did you mean to use 'invariant_reduce_raw()'?"
            ) from e
    return accumulator


def count(
    value: InvariantValue | Any, iterable: Iterable[InvariantValue]
) -> InvariantNumber:
    """Return the number of occurrences of a value in the list."""
    return sum(
        map(
            lambda a: (
                InvariantNumber(1, a.addresses)
                if a == value
                else InvariantNumber(0, a.addresses)
            ),
            iterable,
        )
    )


def match(
    pattern: str, iterable: Iterable[InvariantValue], group_id: int | str = 0
) -> list[InvariantValue]:
    """Match the value against the given regex pattern and return the matched group.

    The function calls .match() on each element of the iterable that has .match() function.

    Args:
        pattern: The regex pattern to match against.
        iterable: The iterable of InvariantValue objects to match against.
        group_id: The group ID to return during the match.
    """
    return reduce(
        lambda a, b: a + b,
        [],
        map(
            lambda a: [g] if (g := a.match(pattern, group_id)) else [],
            filter(lambda a: getattr(a, "match", None) and callable(a.match), iterable),
        ),
    )


def any(  # pylint: disable=redefined-builtin
    iterable: Iterable[InvariantValue],
) -> InvariantBool:
    """Return True if any element in the list is True."""
    return reduce(
        lambda element1, element2: element1 | element2,
        InvariantBool(False, []),
        iterable,
    )


def all(  # pylint: disable=redefined-builtin
    iterable: Iterable[InvariantValue],
) -> InvariantBool:
    """Return True if all elements in the list are True."""
    return reduce(
        lambda element1, element2: element1 & element2,
        InvariantBool(True, []),
        iterable,
    )


def filter(  # pylint: disable=redefined-builtin
    predicate: Callable[[InvariantValue], bool], iterable: Iterable[InvariantValue]
) -> list[InvariantValue]:
    """Filter elements of the list based on a predicate."""
    return [item for item in iterable if predicate(item)]


def find(
    predicate: Callable[[InvariantValue], bool],
    iterable: Iterable[InvariantValue],
    default=None,
) -> InvariantValue:
    """Return the first element matching the predicate or None."""
    for item in iterable:
        if predicate(item):
            return item
    return default


def min(  # pylint: disable=redefined-builtin
    iterable: Iterable[InvariantValue],
) -> InvariantValue:
    """Return the minimum value in the list."""
    return builtin_min(iterable, key=lambda x: x.value)


def max(  # pylint: disable=redefined-builtin
    iterable: Iterable[InvariantValue],
) -> InvariantValue:
    """Return the maximum value in the list."""
    return builtin_max(iterable, key=lambda x: x.value)

  
def len(iterable: Iterable[InvariantValue]) -> InvariantNumber:
    """Return the length of the list."""
    return InvariantNumber(
        builtin_len(iterable), [addr for item in iterable for addr in item.addresses]
    )
