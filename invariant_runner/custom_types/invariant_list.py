"""InvariantDict class definition"""

from collections.abc import Iterable
from typing import Any, Callable, Union

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_value import InvariantValue


def invariant_map(
    func: Callable[[InvariantValue], InvariantValue], iterable: Iterable[InvariantValue]
) -> list[InvariantValue]:
    """Apply a function to each element in the iterable and create a new list."""
    return [func(item) for item in iterable]


def invariant_reduce_raw(
    func: Callable[[Any, Any], Any],
    initial_value: Any,
    iterable: Iterable[InvariantValue],
) -> Any:
    """
    Reduce the list instance to a single value using a function and disregarding address information.
    Use this method instead of 'reduce' when the 'func' is not compatible with 'InvariantValue'.
    """
    # Strip address information from values
    values_ = [item.value for item in iterable]

    accumulator = initial_value
    for item in values_:
        accumulator = func(accumulator, item)
    return accumulator


def invariant_reduce(
    func: Callable[[InvariantValue, InvariantValue], InvariantValue],
    initial_value: Union[InvariantValue, Any],
    iterable: Iterable[InvariantValue],
) -> InvariantValue:
    """Reduce the list instance to a single value using a function."""
    accumulator = initial_value
    for item in iterable:
        try:
            accumulator = func(accumulator, item)
        except TypeError as e:
            raise TypeError(
                f"Incompatible function: {func} for types '{type(accumulator).__name__}' and '{type(item).__name__}'. "
                "Did you mean to use 'invariant_reduce_raw()'?"
            ) from e
    return accumulator


def invariant_count(
    value: Union[InvariantValue, Any], iterable: Iterable[InvariantValue]
) -> InvariantNumber:
    """Return the number of occurrences of a value in the list."""
    return sum(
        invariant_map(
            lambda a: (
                InvariantNumber(1, a.addresses)
                if a == value
                else InvariantNumber(0, a.addresses)
            ),
            iterable,
        )
    )


def invariant_any(iterable: Iterable[InvariantValue]) -> InvariantBool:
    """Return True if any element in the list is True."""
    return invariant_reduce(
        lambda element1, element2: element1 | element2,
        InvariantBool(False, []),
        iterable,
    )


def invariant_all(iterable: Iterable[InvariantValue]) -> InvariantBool:
    """Return True if all elements in the list are True."""
    return invariant_reduce(
        lambda element1, element2: element1 & element2,
        InvariantBool(True, []),
        iterable,
    )


def invariant_filter(
    predicate: Callable[[InvariantValue], bool], iterable: Iterable[InvariantValue]
) -> list[InvariantValue]:
    """Filter elements of the list based on a predicate."""
    return [item for item in iterable if predicate(item)]


def invariant_find(
    predicate: Callable[[InvariantValue], bool],
    iterable: Iterable[InvariantValue],
    default=None,
) -> InvariantValue:
    """Return the first element matching the predicate or None."""
    for item in iterable:
        if predicate(item):
            return item
    return default


def invariant_min(iterable: Iterable[InvariantValue]) -> InvariantValue:
    """Return the minimum value in the list."""
    return min(iterable, key=lambda x: x.value)


def invariant_max(iterable: Iterable[InvariantValue]) -> InvariantValue:
    """Return the maximum value in the list."""
    return max(iterable, key=lambda x: x.value)
