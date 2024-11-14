"""This script is used to run tests using Invariant."""

import argparse
import logging
import os
import sys
import time

import pytest

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


def print_test_summary() -> None:
    """Print a summary of the test results."""
    print(f"{BOLD}Test summary{END}")
    print(f"{BOLD}------------{END}")

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

    # Run pytest with remaining arguments
    pytest.main(pytest_args)
    print_test_summary()
