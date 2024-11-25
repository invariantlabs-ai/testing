"""Defines an Invariant trace."""

from typing import Any, Callable, Dict, List

from invariant_runner.custom_types.invariant_dict import (InvariantDict,
                                                          InvariantValue)
from invariant_runner.custom_types.invariant_list import InvariantList
from pydantic import BaseModel


def iterate_tool_calls(messages: list[dict]):
    for msg_i, msg in enumerate(messages):
        if msg.get("role") != "assistant":
            continue
        for tc_i, tc in enumerate(msg.get("tool_calls", [])):
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
    """
    Match a keyword filter.

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

    @classmethod
    def from_explorer(cls, identifier_or_id: str, index: int | None = None) -> "Trace":
        """
        Loads a public trace from the Explorer (https://explorer.invariantlabs.ai).

        The identifier_or_id can be either a trace ID or a <username>/<dataset> pair, in which case
        the index of the trace to load must be provided.

        :param identifier_or_id: The trace ID or <username>/<dataset> pair.
        :param index: The index of the trace to load from the dataset.

        :return: A Trace object with the loaded trace.
        """
        import requests

        metadata = {
            "id": identifier_or_id,
        }
        timeout = [5, 5]  # connect and read timeouts.

        if index is not None:
            username, dataset = identifier_or_id.split("/")

            trace_metadata = requests.get(
                url=f"https://explorer.invariantlabs.ai/api/v1/dataset/byuser/{username}/{dataset}/traces?indices={index}",
                timeout=timeout,
            )
            if len(trace_metadata.json()) == 0:
                raise ValueError(
                    "No trace with the specified index found for the <username>/<dataset> pair."
                )
            identifier_or_id = trace_metadata.json()[0]["id"]

            metadata.update(
                {
                    "trace_id": identifier_or_id,
                    "dataset": dataset,
                    "username": username,
                }
            )
        else:
            if "/" in identifier_or_id:
                raise ValueError(
                    "Please provide the index of the trace to select from the <username>/<dataset> pair."
                )

        response = requests.get(
            url=f"https://explorer.invariantlabs.ai/api/v1/trace/{identifier_or_id}?annotated=1",
            timeout=timeout,
        )
        return cls(trace=response.json()["messages"], metadata=metadata)

    def messages(
        self, selector: int | None = None, **filterkwargs
    ) -> List[InvariantDict]:
        """Return the messages in the trace."""
        if isinstance(selector, int):
            return InvariantDict(self.trace[selector], f"{selector}")
        if len(filterkwargs) > 0:
            return InvariantList.from_values(
                [
                    InvariantDict(message, [f"{i}"])
                    for i, message in enumerate(self.trace)
                    if all(
                        match_keyword_filter(kwname, kwvalue, message.get(kwname))
                        for kwname, kwvalue in filterkwargs.items()
                    )
                ]
            )
        return InvariantList.from_values(
            [InvariantDict(message, [f"{i}"]) for i, message in enumerate(self.trace)]
        )

    def tool_calls(
        self, selector: int | None = None, **filterkwargs
    ) -> InvariantList | InvariantDict:
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
            return InvariantList.from_values(
                [
                    InvariantDict(tc, tc_address)
                    for tc_address, tc in iterate_tool_calls(self.trace)
                    if all(
                        find_value(tc["function"], kwname) == kwvalue
                        for kwname, kwvalue in selector.items()
                    )
                ]
            )
        elif len(filterkwargs) > 0:
            return InvariantList.from_values(
                [
                    InvariantDict(tc, tc_address)
                    for tc_address, tc in iterate_tool_calls(self.trace)
                    if all(
                        match_keyword_filter_on_tool_call(
                            kwname, kwvalue, tc.get(kwname), tc
                        )
                        for kwname, kwvalue in filterkwargs.items()
                    )
                ]
            )
        else:
            return InvariantList.from_values(
                [
                    InvariantDict(tc, tc_address)
                    for tc_address, tc in iterate_tool_calls(self.trace)
                ]
            )

    def to_python(self):
        """
        Returns a snippet of Python code construct that can be used
        to recreate the trace in a Python script.
        """
        return (
            "Trace(trace=[\n"
            + ",\n".join("  " + str(msg) for msg in self.trace)
            + "\n])"
        )
