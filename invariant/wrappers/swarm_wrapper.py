"""Wrapper for the OpenAI Swarm client."""

import contextvars
import copy

from invariant.custom_types.trace import Trace
from swarm import Swarm
from swarm.types import Response


class SwarmWrapper:
    """Wrapper for the OpenAI Swarm client."""

    def __init__(self, client: Swarm) -> None:
        self.client = client
        self._history_var = contextvars.ContextVar("history")

    @classmethod
    def wrap_swarm(cls, client: Swarm) -> Swarm:
        """Wrap the OpenAI Swarm client."""
        return cls(client)

    def _get_history(self):
        """Get the current context's history."""
        # Ensure the ContextVar has a value for the current context
        try:
            return self._history_var.get()
        except LookupError:
            # If no value is set, initialize it to an empty list
            self._history_var.set([])
            return self._history_var.get()

    def _set_history(self, history):
        """Set the current context's history."""
        self._history_var.set(history)

    def to_invariant_trace(self) -> Trace:
        """Convert the Swarm response to an Invariant Trace."""
        messages = copy.deepcopy(self._get_history())
        return Trace(trace=messages)

    def run(self, *args, **kwargs) -> Response:
        """Call the run method on the Swarm client."""
        # Extract 'messages' from kwargs if provided
        messages = kwargs.get("messages")

        # If 'messages' is not in kwargs, it might be in args
        if messages is None and len(args) > 0:
            messages = args[1]

        # Add messages to the context-specific history
        if messages:
            current_history = self._get_history()
            current_history.extend(messages)
            self._set_history(current_history)

        response = self.client.run(*args, **kwargs)
        current_history = self._get_history()
        if isinstance(response, Response):
            current_history.extend(response.messages)
        elif isinstance(response, dict):
            current_history.extend(response.get("response", {}).get("messages", []))
        self._set_history(current_history)
        return response
