"""Contains sample tests which use the Invariant Runner."""

import pytest
from invariant_runner.manager import Manager


@pytest.mark.skip(reason="skipping")
def test_agent_response():
    """Test agent response."""
    with Manager() as _:
        assert True


@pytest.mark.parametrize(
    "parameter_1, parameter_2",
    [
        ("parameter_1_value_1", "parameter_2_value_1"),
        ("parameter_1_value_2", "parameter_2_value_2"),
        ("parameter_1_value_1", "parameter_2_value_2"),
    ],
)
def test_another_agent_response(request, parameter_1, parameter_2):
    """Test another agent response."""
    with Manager() as _:
        assert True
