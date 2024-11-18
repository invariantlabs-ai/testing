"""Defines an Invariant trace."""

from typing import Dict, List, Any, Callable

from pydantic import BaseModel

from invariant_runner.custom_types.invariant_dict import InvariantDict, InvariantValue
from invariant_runner.custom_types.invariant_list import InvariantList


def iterate_tool_calls(messages: list[dict]):
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            yield tc


def match_keyword_filter_on_tool_call(kwname: str, kwvalue: str | int | Callable, value: InvariantValue | Any, tool_call: dict) -> bool:
    # redirect checks on name, arguments and id to the 'function' sub-dictionary
    # this enables checks like tool_calls(name='greet') to work
    if kwname in ["name", "arguments", "id"]:
        value = tool_call["function"].get(kwname)
    return match_keyword_filter(kwname, kwvalue, value)


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

    
class Trace(BaseModel):
    """Defines an Invariant trace."""

    trace: List[Dict]

    def messages(self, selector: int | None = None, **filterkwargs) -> List[InvariantDict]:
        """Return the messages in the trace."""
        if type(selector) is int:
            return InvariantDict(self.trace[selector], f"{selector}")
        elif len(filterkwargs) > 0:
            return InvariantList.from_values([InvariantDict(message, [f"{i}"]) for i, message in enumerate(self.trace) if all(
                match_keyword_filter(kwname, kwvalue, message.get(kwname)) for kwname, kwvalue in filterkwargs.items())])
        else:
            return InvariantList.from_values([InvariantDict(message, [f"{i}"]) for i, message in enumerate(self.trace)])

    def tool_calls(self, selector: int | None = None, **filterkwargs) -> List[InvariantDict]:
        """Return the tool calls in the trace."""
        for tc in iterate_tool_calls(self.trace):
            if type(selector) is int:
                for i, tc in enumerate(iterate_tool_calls(self.trace)):
                    if i == selector:
                        return InvariantDict(tc, f"{i}")
            elif len(filterkwargs) > 0:
                return InvariantList.from_values([InvariantDict(tc, [f"{i}"]) for i, tc in enumerate(iterate_tool_calls(self.trace)) if all(
                    match_keyword_filter_on_tool_call(kwname, kwvalue, tc.get(kwname), tc) for kwname, kwvalue in filterkwargs.items())])
            else:
                return InvariantList.from_values([InvariantDict(tc, [f"{i}"]) for i, tc in enumerate(iterate_tool_calls(self.trace))])
