"""Wrapper for the OpenAI Swarm client."""

import copy

from invariant.custom_types.trace import Trace
from swarm import Swarm
from swarm.types import Response


class SwarmWrapper:
    """Wrapper for the OpenAI Swarm client."""

    def __init__(self, client: Swarm) -> None:
        self.client = client
        self.history = []

    @classmethod
    def wrap_swarm(cls, client: Swarm) -> Swarm:
        """Wrap the OpenAI Swarm client."""
        return cls(client)

    def to_invariant_trace(self) -> Trace:
        """Convert the Swarm response to an Invariant Trace."""
        messages = copy.deepcopy(self.history)
        return Trace(trace=messages)

    def run(self, *args, **kwargs) -> Response:
        """Call the run method on the Swarm client."""
        # Extract 'messages' from kwargs if provided
        messages = kwargs.get("messages")

        # If 'messages' is not in kwargs, it might be in args
        if messages is None and len(args) > 0:
            messages = args[1]

        if messages:
            self.history.extend(messages)

        response = self.client.run(*args, **kwargs)
        if isinstance(response, Response):
            self.history.extend(response.messages)
        elif isinstance(response, dict):
            # If stream is set to True, the response is a dict with a 'response' key
            self.history.extend(response.get("response", {}).get("messages", []))
        return response
