"""Define a context manager class to run tests with Invariant."""

import inspect
import json
import logging
import os
import time
from contextvars import ContextVar
from json import JSONEncoder

import pytest
from invariant_sdk.client import Client as InvariantClient
from invariant_sdk.types.push_traces import PushTracesResponse
from pydantic import ValidationError

from invariant_runner import utils
from invariant_runner.config import Config
from invariant_runner.constants import INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR
from invariant_runner.custom_types.test_result import AssertionResult, TestResult
from invariant_runner.formatter import format_trace

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INVARIANT_CONTEXT = ContextVar("invariant_context", default=[])


class Manager:
    """Context manager class to run tests with Invariant."""

    def __init__(self, trace):
        self.trace = trace
        self.assertions: list[AssertionResult] = []
        self.explorer_url = ""

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
            explorer_url=self.explorer_url,
        )

    def _get_explorer_url(self, push_traces_response: PushTracesResponse) -> str:
        """Get the Explorer URL for the test results."""
        prefix = (
            "https://localhost"
            if self.client.api_url == "http://localhost:8000"
            else self.client.api_url
        )
        return (
            f"{prefix}/u/{push_traces_response.username}/{self.config.dataset_name}/t/1"
        )

    def __enter__(self) -> "Manager":
        """Enter the context manager and setup configuration."""
        INVARIANT_CONTEXT.get().append(self)
        self.config = self._load_config()  # pylint: disable=attribute-defined-outside-init
        self.test_name = self._get_test_name()  # pylint: disable=attribute-defined-outside-init
        self.client = (  # pylint: disable=attribute-defined-outside-init
            InvariantClient() if self.config is not None and self.config.push else None
        )

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
            push_traces_response = self.push()
            self.explorer_url = self._get_explorer_url(push_traces_response)  # pylint: disable=attribute-defined-outside-init

        # make sure path exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(self._get_test_result().model_dump(), file, cls=TestResultEncoder)
            file.write("\n")

        # Handle exceptions via exc_value, if needed
        # Returning False allows exceptions to propagate; returning True suppresses them
        INVARIANT_CONTEXT.get().pop()

        # unset 'manager' field of parent Trace
        if self.trace.manager is self:
            self.trace.manager = None

        # handle outcome (e.g. throw an exception if a hard assertion failed)
        self.handle_outcome()

        return False

    def handle_outcome(self):
        # collect set of failed hard assertions
        failed_hard_assertions = [
            a for a in self.assertions if a.type == "HARD" and not a.passed
        ]

        # raise a pytest failure if there are any failed hard assertions
        if len(failed_hard_assertions) > 0:
            # the error message is all failed hard assertions with respective
            # code and trace snippets
            error_message = (
                f"ERROR: {len(failed_hard_assertions)} hard assertions failed:\n\n"
            )

            for i, failed_assertion in enumerate(failed_hard_assertions):
                test_snippet = failed_assertion.test
                message = failed_assertion.message
                # flatten addresses
                addresses = failed_assertion.addresses
                # remove character ranges after : in addresses
                addresses = [a.split(":")[0] if ":" in a else a for a in addresses]

                column_width = utils.terminal_width()
                failure_message = (
                    "ASSERTION FAILED"
                    if failed_assertion.type == "HARD"
                    else "EXPECTATION VIOLATED"
                )

                formatted_trace = format_trace(self.trace.trace, highlights=addresses)
                if formatted_trace is not None:
                    error_message += (
                        " "
                        + test_snippet
                        + ("_" * column_width + "\n")
                        + f"\n{failure_message}: {message or ''}\n"
                        + ("_" * column_width + "\n\n")
                        + formatted_trace
                        + "\n"
                    )

                # add separator between failed assertions
                if i < len(failed_hard_assertions) - 1:
                    error_message += "_" * column_width + "\n\n"

            pytest.fail(error_message, pytrace=False)

    def push(self) -> PushTracesResponse:
        """Push the test results to Explorer."""
        assert self.config is not None, "cannot push(...) without a config"

        # annotations have the following structure:
        # {content: str, address: str, extra_metadata: {source: str, test: str, line: int}}
        annotations = []
        for assertion in self.assertions:
            assertion_id = id(assertion)

            for address in assertion.addresses:
                source = (
                    "test-assertion" if assertion.type == "HARD" else "test-expectation"
                )
                if assertion.passed:
                    source += "-passed"

                annotations.append(
                    {
                        "address": "messages." + address,
                        "content": assertion.message or str(assertion),
                        "extra_metadata": {
                            "source": source,
                            "test": assertion.test,
                            "passed": assertion.passed,
                            "line": 0,
                            # ID of the assertion (if an assertion results in multiple annotations)
                            "assertion_id": assertion_id,
                        },
                    }
                )

        test_result = self._get_test_result()
        metadata = {
            "name": test_result.name,
            "invariant.num-failures": len(
                [a for a in self.assertions if a.type == "HARD" and not a.passed]
            ),
            "invariant.num-warnings": len(
                [a for a in self.assertions if a.type == "SOFT" and not a.passed]
            ),
        }

        try:
            return self.client.create_request_and_push_trace(
                messages=[self.trace.trace],
                annotations=[annotations],
                metadata=[metadata],
                dataset=self.config.dataset_name,
                request_kwargs={"verify": utils.ssl_verification_enabled()},
            )
        except Exception:
            # fail test suite hard if this happens
            pytest.fail(
                "Failed to push test results to Explorer. Please make sure your Invariant API key and endpoint are setup correctly or run without --push.",
                pytrace=False,
            )


class TestResultEncoder(JSONEncoder):
    """
    Simple encoder that omits the Manager object from the JSON output.
    """

    def default(self, o):
        if isinstance(o, Manager):
            return None
        return JSONEncoder.default(self, o)
