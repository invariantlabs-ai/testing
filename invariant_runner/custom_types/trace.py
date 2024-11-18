"""Defines an Invariant trace."""

from typing import Dict, List, Any, Callable

from pydantic import BaseModel

from invariant_runner.custom_types.invariant_dict import InvariantDict, InvariantValue


class Trace(BaseModel):
    """Defines an Invariant trace."""

    trace: List[Dict]

    def messages(self, selector: int | None = None, **filterkwargs) -> List[InvariantDict]:
        """Return the messages in the trace."""
        if type(selector) is int:
            return InvariantDict(self.trace[selector], f"{selector}")
        elif len(filterkwargs) > 0:
            return [InvariantDict(message, f"{i}") for i, message in enumerate(self.trace) if all(
                match_keyword_filter(kwname, kwvalue, message.get(kwname)) for kwname, kwvalue in filterkwargs.items())]

        return [InvariantDict(message, f"{i}") for i, message in enumerate(self.trace)]


def match_keyword_filter(kwname: str, kwvalue: str | int | Callable, value: InvariantValue | Any) -> bool:
    """
    Match a keyword filter.
    
    A keyword filter such as name='value' can be one of the following:
    - a string or integer value to compare against exactly
    - a lambda function to apply to the value to check for more complex conditions
    
    """
    if isinstance(value, InvariantValue):
        value = value.value
    
    # compare by value or use a lambda function
    if isinstance(kwvalue, str) or isinstance(kwvalue, int):
        return kwvalue == value
    elif callable(kwvalue):
        return kwvalue(value)
    raise ValueError(f"Cannot filter '{kwname}' with '{kwvalue}' (only str/int comparison or lambda functions are supported)")

    