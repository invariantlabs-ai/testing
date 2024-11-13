"""This script is used to run tests using Invariant."""

import argparse
import os
import sys
import time

import pytest

from invariant_runner.config import Config

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
        INVARIANT_API_KEY environment variable must be set. Visit 
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
    api_key = os.getenv("INVARIANT_API_KEY")

    dataset_name = args.dataset_name or f"dataset_{int(time.time())}"

    return Config(
        dataset_name=dataset_name,
        push=args.push,
        api_key=api_key,
    )


if __name__ == "__main__":
    try:
        # Parse command-line arguments and create configuration
        invariant_runner_args, pytest_args = parse_args()
        config = create_config(invariant_runner_args)
    except ValueError as e:
        print("Configuration error:", e)
        sys.exit(1)

    # Run pytest with remaining arguments
    pytest.main(pytest_args)
