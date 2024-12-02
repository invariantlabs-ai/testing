"""Defines an Invariant trace."""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, Generator, List

from pydantic import BaseModel

from invariant.custom_types.invariant_dict import InvariantDict, InvariantValue
from invariant.utils.explorer import from_explorer


def iterate_tool_calls(
    messages: list[dict],
) -> Generator[tuple[list[str], dict], None, None]:
    """Generator function to iterate over tool calls in a list of messages.

    Yields:
        tuple[list[str], dict]: A tuple containing:
            - A list of strings representing the hierarchical address of the tool call
              in the message. For example, `["1.tool_calls.0"]` indicates the first tool
              call in the second message.
            - The tool call data (a dictionary or object representing the tool call).

    Example:
        messages = [
            {"role": "user", "content": "What's the weather?"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "weather_tool",
                            "arguments": {"location": "NYC"}
                        },
                        "id": "call_1",
                        "type": "function"
                    }
                ]
            }
        ]

        for address, tool_call in iterate_tool_calls(messages):
            print(address, tool_call)

        Output:
            ['1.tool_calls.0'] {'function': {'name': 'weather_tool', 'arguments': {'location':
            'NYC'}}, 'id': 'call_1', 'type': 'function'}
    """
    for msg_i, msg in enumerate(messages):
        if msg.get("role") != "assistant":
            continue
        tool_calls = msg.get("tool_calls") or []
        for tc_i, tc in enumerate(tool_calls):
            yield ([f"{msg_i}.tool_calls.{tc_i}"], tc)


def match_keyword_filter_on_tool_call(
    kwname: str,
    kwvalue: str | int | Callable,
    value: InvariantValue | Any,
    tool_call: dict,
) -> bool:
    # redirect checks on name, arguments and id to the 'function' sub-dictionary
    # this enables checks like tool_calls(name='greet') to work
    if kwname in ["name", "arguments", "id"]:
        value = tool_call["function"].get(kwname)
    return match_keyword_filter(kwname, kwvalue, value)


def match_keyword_filter(
    kwname: str, kwvalue: str | int | Callable, value: InvariantValue | Any
) -> bool:
    """Match a keyword filter.

    A keyword filter such as name='value' can be one of the following:
    - a string or integer value to compare against exactly
    - a lambda function to apply to the value to check for more complex conditions

    """
    if isinstance(value, InvariantValue):
        value = value.value

    # compare by value or use a lambda function
    if isinstance(kwvalue, (str, int)):
        return kwvalue == value
    if callable(kwvalue):
        return kwvalue(value)
    raise ValueError(
        f"Cannot filter '{kwname}' with '{kwvalue}' (only str/int comparison or lambda functions are supported)"
    )


class Trace(BaseModel):
    """Defines an Invariant trace."""

    trace: List[Dict]
    metadata: Dict[str, Any] | None = None

    # Active Manager that is running with this trace as context
    # (e.g. with Trace(...) as trace: ... )
    # If this is already assigned, the trace is currently being used in a context manager already and should not be re-used.
    manager: Any = None

    def as_context(self):
        from invariant.manager import Manager

        if self.manager is None:
            self.manager = Manager(self)
        return self.manager

    def run_assertions(self, assertions: list[Callable[Trace, Any]]):
        """Runs a list of assertions on the trace. Assertions are run by providing a list of functions,
        each taking Trace object as a single argument.

        Args:
            assertions: A list of functions taking Trace as a single argument
        """
        for assertion in assertions:
            assertion(self)

    @classmethod
    def from_explorer(
        cls,
        identifier_or_id: str,
        index: int | None = None,
        explorer_endpoint: str = "https://explorer.invariantlabs.ai",
    ) -> "Trace":
        """Loads a public trace from the Explorer (https://explorer.invariantlabs.ai).

        The identifier_or_id can be either a trace ID or a <username>/<dataset> pair, in which case
        the index of the trace to load must be provided.

        :param identifier_or_id: The trace ID or <username>/<dataset> pair.
        :param index: The index of the trace to load from the dataset.

        :return: A Trace object with the loaded trace.
        """
        messages, metadata = from_explorer(identifier_or_id, index, explorer_endpoint)
        return cls(trace=messages, metadata=metadata)

    def messages(
        self, selector: int | None = None, **filterkwargs
    ) -> list[InvariantDict]:
        """Return the messages in the trace."""
        if isinstance(selector, int):
            return InvariantDict(self.trace[selector], f"{selector}")
        if len(filterkwargs) > 0:
            return [
                InvariantDict(message, [f"{i}"])
                for i, message in enumerate(self.trace)
                if all(
                    match_keyword_filter(kwname, kwvalue, message.get(kwname))
                    for kwname, kwvalue in filterkwargs.items()
                )
            ]
        return [
            InvariantDict(message, [f"{i}"]) for i, message in enumerate(self.trace)
        ]

    def tool_pairs(self) -> list[tuple[InvariantDict, InvariantDict]]:
        """Returns the list of tuples of (tool_call, tool_output)."""
        res = []
        for msg_idx, msg in enumerate(self.trace):
            if msg.get("role") != "assistant":
                continue
            for tc_idx, tc in enumerate(msg.get("tool_calls", [])):
                res.append(
                    (
                        msg_idx,
                        InvariantDict(tc, [f"{msg_idx}.tool_calls.{tc_idx}"]),
                        None,
                    )
                )

        matched_ids = set()
        # First, find all tool outputs that have the same id as a tool call
        for msg_idx, msg in enumerate(self.trace):
            if msg.get("role") != "tool" or "id" not in msg:
                continue
            for i, res_pair in enumerate(res):
                if res_pair[1].get("id") == msg.get("id"):
                    res[i] = (i, res_pair[1], InvariantDict(msg, [f"{msg_idx}"]))
                    matched_ids.add(msg.get("id"))

        res = sorted(res, key=lambda x: x[0])

        # For the remaining tool outputs, assign them to the previous unmatched tool call
        for msg_idx, msg in enumerate(self.trace):
            if msg.get("role") != "tool":
                continue
            if msg.get("id") in matched_ids:
                continue
            for i, res_pair in reversed(list(enumerate(res))):
                tool_call_idx, tool_call, tool_out = res_pair
                if tool_out is None and tool_call_idx < msg_idx:
                    res[i] = (
                        tool_call_idx,
                        tool_call,
                        InvariantDict(msg, [f"{msg_idx}"]),
                    )
                    break

        return [
            (res_pair[1], res_pair[2]) for res_pair in res if res_pair[2] is not None
        ]

    def tool_calls(
        self, selector: int | None = None, **filterkwargs
    ) -> list[InvariantDict] | InvariantDict:
        """Return the tool calls in the trace."""
        if isinstance(selector, int):
            for i, (tc_address, tc) in enumerate(iterate_tool_calls(self.trace)):
                if i == selector:
                    return InvariantDict(tc, tc_address)
        elif isinstance(selector, dict):

            def find_value(d, path):
                for k in path.split("."):
                    d = d[k]
                return d

            return [
                InvariantDict(tc, tc_address)
                for tc_address, tc in iterate_tool_calls(self.trace)
                if all(
                    find_value(tc["function"], kwname) == kwvalue
                    for kwname, kwvalue in selector.items()
                )
            ]
        elif len(filterkwargs) > 0:
            return [
                InvariantDict(tc, tc_address)
                for tc_address, tc in iterate_tool_calls(self.trace)
                if all(
                    match_keyword_filter_on_tool_call(
                        kwname, kwvalue, tc.get(kwname), tc
                    )
                    for kwname, kwvalue in filterkwargs.items()
                )
            ]
        else:
            return [
                InvariantDict(tc, tc_address)
                for tc_address, tc in iterate_tool_calls(self.trace)
            ]

    def __str__(self):
        return "\n".join(str(msg) for msg in self.trace)
