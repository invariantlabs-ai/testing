"""Utility functions for the invariant runner."""

from invariant_runner.config import Config
from invariant_runner.constants import INVARIANT_RUNNER_TEST_RESULTS_DIR


def get_test_results_file_path(config: Config) -> str:
    """Get the file path for the test results."""
    return (
        f"{INVARIANT_RUNNER_TEST_RESULTS_DIR}/results_for_{config.dataset_name}.jsonl"
    )
