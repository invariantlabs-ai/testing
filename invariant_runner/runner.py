"""This script is used to run tests using Invariant."""

import argparse
import json
import logging
import os
import sys
import time

import pytest
from invariant_sdk.client import Client as InvariantClient

from invariant_runner import utils
from invariant_runner.config import Config
from invariant_runner.constants import (
    INVARIANT_AP_KEY_ENV_VAR,
    INVARIANT_RUNNER_TEST_RESULTS_DIR,
    INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR,
    INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANSI escape code for bold text
BOLD = "\033[1m"
END = "\033[0m"


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    """Parse command-line arguments for the Invariant Runner."""
    parser = argparse.ArgumentParser(
        description="Run tests with Invariant Runner configuration."
    )
    parser.add_argument(
        "--dataset_name",
        help="The name of the dataset to be used to associate the test trace data and results. This name will be used to derive a fresh dataset name on each run (e.g. myproject-1732007573)",
        default="tests",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="""Flag to indicate whether to push data to the invariant server. If set to true,
        {INVARIANT_AP_KEY_ENV_VAR} environment variable must be set. Visit
        {BOLD}https://explorer.invariantlabs.ai/docs/{END} to see steps to generate
        an API key.""",
    )
    return parser.parse_known_args()


def create_config(args: argparse.Namespace) -> Config:
    """Create and return a Config instance based on parsed arguments and environment variables.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        Config: Config instance with dataset name, push status, and API key.
    """
    api_key = os.getenv(INVARIANT_AP_KEY_ENV_VAR)

    prefix = args.dataset_name
    dataset_name = f"{prefix}-{int(time.time())}"

    os.makedirs(INVARIANT_RUNNER_TEST_RESULTS_DIR, exist_ok=True)

    return Config(
        dataset_name=dataset_name,
        push=args.push,
        api_key=api_key,
        result_output_dir=INVARIANT_RUNNER_TEST_RESULTS_DIR,
    )


def finalize_tests_and_print_summary(conf: Config) -> None:
    """
    Finalizes the test run:
    * pushes result metadata to the Explorer if --push
    * prints a summary of the test results.
    """
    file_path = utils.get_test_results_file_path(conf.dataset_name)

    if not os.path.exists(file_path):
        print(
            "[ERROR] No test results found. Make sure your tests were executed correctly using Invariant assertions."
        )
        return

    print(f"{BOLD}Invariant Test summary{END}")
    print(f"Test result saved to: {file_path}")
    print(f"{BOLD}------------{END}")

    passed_count = 0
    tests = 0
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            test_result = json.loads(line.strip())
            tests += 1
            if test_result.get("passed"):
                passed_count += 1
            print(
                f"{tests}. {test_result.get('name')}: {'PASSED' if test_result.get('passed') else 'FAILED'}"
            )
    print("\n")
    print(f"{BOLD}Total tests: {END}{tests}")
    print(f"{BOLD}Passed: {END}: {passed_count}")
    print(f"{BOLD}Failed: {END}: {tests - passed_count}")
    print(f"{BOLD}------------{END}")

    # update dataset metadata if --push
    if conf.push:
        client = InvariantClient()
        client.create_request_and_update_dataset_metadata(
            dataset_name=conf.dataset_name,
            metadata={
                "invariant_test_results": {
                    "num_tests": tests,
                    "num_passed": passed_count,
                }
            },
            request_kwargs={"verify": utils.ssl_verification_enabled()},
        )

        print(
            f"Results available at {client.api_url}/u/developer/{conf.dataset_name}/t/1"
        )


if __name__ == "__main__":
    try:
        # Parse command-line arguments and create configuration
        invariant_runner_args, pytest_args = parse_args()
        config = create_config(invariant_runner_args)
        os.environ[INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR] = config.model_dump_json()
        # pass along actual terminal width to the test runner (for better formatting)
        os.environ[INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR] = str(
            utils.terminal_width()
        )
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)

    test_results_file_path = utils.get_test_results_file_path(config.dataset_name)
    if os.path.exists(test_results_file_path):
        os.remove(test_results_file_path)

    # Run pytest with remaining arguments
    pytest.main(pytest_args)

    # print Invariant test summary
    finalize_tests_and_print_summary(config)

    # Update dataset level metadata to include the total passed and failed counts.
