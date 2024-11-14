"""This script is used to run tests using Invariant."""

import argparse
import json
import logging
import os
import sys
import time

import pytest

from invariant_runner import utils
from invariant_runner.config import Config
from invariant_runner.constants import (
    INVARIANT_AP_KEY_ENV_VAR,
    INVARIANT_RUNNER_TEST_RESULTS_DIR,
    INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR,
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
        help="The name of the dataset to be used to associate the test trace data and results",
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

    dataset_name = args.dataset_name or f"dataset_{int(time.time())}"

    os.makedirs(INVARIANT_RUNNER_TEST_RESULTS_DIR, exist_ok=True)

    return Config(
        dataset_name=dataset_name,
        push=args.push,
        api_key=api_key,
        result_output_dir=INVARIANT_RUNNER_TEST_RESULTS_DIR,
    )


def print_test_summary(conf: Config) -> None:
    """Print a summary of the test results."""

    print(f"{BOLD}Test summary{END}")
    file_path = utils.get_test_results_file_path(conf)
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


if __name__ == "__main__":
    try:
        # Parse command-line arguments and create configuration
        invariant_runner_args, pytest_args = parse_args()
        config = create_config(invariant_runner_args)
        os.environ[INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR] = config.model_dump_json()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)

    test_results_file_path = utils.get_test_results_file_path(config)
    if os.path.exists(test_results_file_path):
        os.remove(test_results_file_path)

    # Run pytest with remaining arguments
    pytest.main(pytest_args)
    print_test_summary(config)

    # Update dataset level metadata to include the total passed and failed counts.
