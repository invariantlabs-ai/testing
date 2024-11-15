"""Defines an Invariant trace."""

from typing import Dict, List

from pydantic import BaseModel

from invariant_runner.custom_types.invariant_dict import InvariantDict


class Trace(BaseModel):
    """Defines an Invariant trace."""

    trace: List[Dict]

    def messages(self):
        """Return the messages in the trace."""
        return [InvariantDict(message, f"{i}") for i, message in enumerate(self.trace)]
