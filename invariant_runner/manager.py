"""Define a context manager class to run tests with Invariant."""

import inspect
import json
import logging
import os
import time
from contextvars import ContextVar

from pydantic import ValidationError

from invariant_runner import utils
from invariant_runner.config import Config
from invariant_runner.constants import INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR
from invariant_runner.custom_types.test_result import TestResult, AssertionResult
from invariant_sdk.client import Client as InvariantClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INVARIANT_CONTEXT = ContextVar("invariant_context", default=[])


class Manager:
    """Context manager class to run tests with Invariant."""

    def __init__(self, trace):
        self.trace = trace
        self.assertions: list[AssertionResult] = []

    @staticmethod
    def current():
        """Return the current context."""
        return INVARIANT_CONTEXT.get()[-1]

    def _get_test_name(self):
        """Retrieve the name of the current test function."""
        frame = inspect.currentframe().f_back.f_back
        # If request fixture is an argument to the test function, use that to get the test
        # function name (with the parameters).
        # This gives the test name in the format: test_name[param1-param2-...] from pytest.
        request = frame.f_locals.get("request")
        if request:
            return request.node.name
        # Fallback to just the test function name.
        return inspect.stack()[2].function

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
        # If no config is provided, the tests have not been invoked with the Invariant test runner.
        return None

    def _get_test_result(self):
        """Generate the test result."""
        passed = all(
            assertion.passed if assertion.type == "HARD" else True
            for assertion in self.assertions
        )
        return TestResult(
            name=self.test_name,
            passed=passed,
            trace=self.trace,
            assertions=self.assertions,
        )

    def __enter__(self) -> "Manager":
        """Enter the context manager and setup configuration."""
        INVARIANT_CONTEXT.get().append(self)
        self.config = self._load_config()  # pylint: disable=attribute-defined-outside-init
        self.test_name = self._get_test_name()  # pylint: disable=attribute-defined-outside-init
        # Fetch the assertions and evaluate them.
        # Store the result in some state and write it to the file as part of __exit__.

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context manager, handling any exceptions that occurred."""
        # Save test result to the output directory.
        dataset_name_for_output_file = (
            self.config.dataset_name if self.config else int(time.time())
        )
        file_path = utils.get_test_results_file_path(dataset_name_for_output_file)
        
        # if there is a config, and push is enabled, push the test results to Explorer
        if self.config is not None and self.config.push:
            self.push()

        # make sure path exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(self._get_test_result().model_dump(), file)
            file.write("\n")

        # Handle exceptions via exc_value, if needed
        # Returning False allows exceptions to propagate; returning True suppresses them
        INVARIANT_CONTEXT.get().pop()
        return True


    def push(self):
        """Push the test results to Explorer."""
        client = InvariantClient()
        
        # annotations have the following structure:
        # {content: str, address: str, extra_metadata: {source: str, test: str, line: int}}
        annotations = []
        for assertion in self.assertions:
            assertion_id = id(assertion)

            for address in assertion.addresses:
                source = "test-assertion" if assertion.type == "HARD" else "test-expectation"
                if assertion.passed:
                    source += "-passed"

                annotations.append({
                    "address": "messages." + address,
                    "content": assertion.message or str(assertion),
                    "extra_metadata": {
                        "source": source,
                        "test": "<not supported yet>",
                        "passed": assertion.passed,
                        "line": 0,
                        # ID of the assertion (if an assertion results in multiple annotations)
                        "assertion_id": assertion_id
                    }
                })

        test_result = self._get_test_result()
        metadata = {
            "name": test_result.name,
            "invariant.num-failures": len([a for a in self.assertions if a.type == "HARD" and not a.passed]),
            "invariant.num-warnings": len([a for a in self.assertions if a.type == "SOFT" and not a.passed]),
        }

        result = client.create_request_and_push_trace(
            messages=[self.trace.trace], 
            annotations=[annotations],
            metadata=[metadata],
            dataset="my-project-20241114-09-53-00",
            # for pros, set verify to False
            request_kwargs={"verify": False}
        )

        print(result, flush=True)


