"""Defines an Invariant trace."""

from typing import Any, Callable, Dict, List

from pydantic import BaseModel

from invariant.custom_types.invariant_dict import InvariantDict, InvariantValue


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

    # Active Manager that is running with this trace as context
    # (e.g. with Trace(...) as trace: ... )
    # If this is already assigned, the trace is currently being used in a context manager already and should not be re-used.
    manager: Any = None

    def as_context(self):
        from invariant.manager import Manager

        if self.manager is None:
            self.manager = Manager(self)
        return self.manager

    @classmethod
    def from_explorer(
        cls,
        identifier_or_id: str,
        index: int | None = None,
        explorer_endpoint: str = "https://explorer.invariantlabs.ai",
    ) -> "Trace":
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
        timeout = 5  # connect and read timeouts.

        if index is not None:
            username, dataset = identifier_or_id.split("/")

            trace_metadata = requests.get(
                url=f"{explorer_endpoint}/api/v1/dataset/byuser/{username}/{dataset}/traces?indices={index}",
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

        print(f"{explorer_endpoint}/api/v1/trace/{identifier_or_id}?annotated=1")
        response = requests.get(
            url=f"{explorer_endpoint}/api/v1/trace/{identifier_or_id}?annotated=1",
            timeout=timeout,
        )
        return cls(trace=response.json()["messages"], metadata=metadata)

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

    def __str__(self):
        return "\n".join(str(msg) for msg in self.trace)
