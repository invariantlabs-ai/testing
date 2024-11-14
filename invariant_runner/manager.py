"""Define a context manager class to run tests with Invariant."""

import inspect
import os

from pydantic import ValidationError

from invariant_runner.config import Config
from invariant_runner.constants import INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR


class Manager:
    """Context manager class to run tests with Invariant."""

    def _get_test_name(self):
        frame = inspect.currentframe().f_back.f_back
        request = frame.f_locals.get("request")
        if request:
            return request.node.name
        raise ValueError(
            """pytest request fixture has to be an argument to the pytest test function 
            where the invariant_runner.Manager is used."""
        )

    def _load_config(self):
        if os.getenv(INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR) is not None:
            try:
                return Config.model_validate_json(
                    os.getenv(INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR)
                )
            except ValidationError as e:
                raise ValueError(
                    f"""The {INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR} environment variable is
                    not a valid configuration."""
                ) from e
        raise ValueError(
            f"The {INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR} environment variable is not set."
        )

    def __enter__(self):
        config = self._load_config()
        test_name = self._get_test_name()
        print(f"Running test: {test_name}")
        print(f"Using configuration: {config}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting context")
        # Handle exceptions via exc_value, if needed
        # Returning False allows exceptions to propagate; returning True suppresses them
        return True
