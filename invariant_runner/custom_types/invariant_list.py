"""InvariantDict class definition"""
from typing import Callable, Any, Union

from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_value import InvariantValue
from collections.abc import Iterable

def invariant_map(func: Callable[[InvariantValue], InvariantValue], iterable: Iterable) -> list:
    """Apply a function to each element in the iterable and create a new list."""
    return [func(item) for item in iterable]


def invariant_reduce_raw(func: Callable[[Any, Any], Any], initial_value: Any, iterable: Iterable) -> Any:
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
    iterable: Iterable
) -> InvariantValue:
    """Reduce the list instance to a single value using a function."""
    accumulator = initial_value
    for item in iterable:
        try:
            accumulator = func(accumulator, item)
        except TypeError as e:
            raise TypeError(
                f"Incompatible function: {func} for types '{type(accumulator).__name__}' and '{type(item).__name__}'. "
                "Did you mean to use '.reduce_raw()'?"
            ) from e
    return accumulator

def invariant_count(value: Union[InvariantValue, Any], iterable: Iterable) -> InvariantNumber:
    """Return the number of occurrences of a value in the list."""
    return sum(invariant_map(
        lambda a: InvariantNumber(1, a.addresses)
        if a == value
        else InvariantNumber(0, a.addresses),
        iterable
    ))

def invariant_any(iterable: Iterable) -> InvariantBool:
    """Return True if any element in the list is True."""
    return invariant_reduce(lambda element1, element2: element1 | element2, InvariantBool(False, []), iterable)

def invariant_all(iterable: Iterable) -> InvariantBool:
    """Return True if all elements in the list are True."""
    return invariant_reduce(lambda element1, element2: element1 & element2, InvariantBool(True, []), iterable)
