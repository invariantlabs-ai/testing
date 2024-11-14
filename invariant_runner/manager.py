"""Define a context manager class to run tests with Invariant."""

import inspect
import json
import logging
import os

from pydantic import ValidationError

from invariant_runner import utils
from invariant_runner.config import Config
from invariant_runner.constants import INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR
from invariant_runner.test_result.assertion import Assertion
from invariant_runner.test_result.result import TestResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Manager:
    """Context manager class to run tests with Invariant."""

    def _get_test_name(self):
        """Retrieve the name of the current test function."""
        frame = inspect.currentframe().f_back.f_back
        request = frame.f_locals.get("request")
        if request:
            return request.node.name
        raise ValueError(
            """pytest request fixture has to be an argument to the pytest test function 
            where the invariant_runner.Manager is used."""
        )

    def _load_config(self):
        """Load the configuration from the environment variable."""
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

    def _get_test_result(self):
        """Run the test and return the test result."""
        # Contains random assertions for demonstration purposes.
        assertions = [
            Assertion(
                type="HARD",
                passed=True,
                content="assert len(xyz) == 3",
            ),
            Assertion(
                type="SOFT",
                passed=False,
                content="assert len(abc) <= 1",
            ),
        ]
        passed = all(
            assertion.passed if assertion.type == "HARD" else True
            for assertion in assertions
        )
        return TestResult(
            name=self.test_name,
            passed=passed,
            trace=[
                {
                    "role": "user",
                    "content": "What are the top 5 best-selling products in 2022",
                }
            ],
            assertions=assertions,
        )

    def __enter__(self) -> "Manager":
        """Enter the context manager and setup configuration."""
        self.config = self._load_config()  # pylint: disable=attribute-defined-outside-init
        self.test_name = self._get_test_name()  # pylint: disable=attribute-defined-outside-init
        logger.info("Running test via Invariant test runner: %s", self.test_name)

        # Fetch the assertions and evaluate them.
        # Store the result in some state and write it to the file as part of __exit__.

        if self.config.push:
            # Push the test results to the Invariant server.
            pass

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context manager, handling any exceptions that occurred."""
        # Save test result to the output directory.
        file_path = utils.get_test_results_file_path(self.config)
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(self._get_test_result().model_dump(), file)
            file.write("\n")

        # Handle exceptions via exc_value, if needed
        # Returning False allows exceptions to propagate; returning True suppresses them
        return True
