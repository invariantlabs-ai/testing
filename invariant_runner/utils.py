"""Utility functions for the invariant runner."""

import os

from constants import INVARIANT_RUNNER_TEST_RESULTS_DIR


def get_test_results_file_path(dataset_name: str) -> str:
    """Get the file path for the test results."""
    return f"{INVARIANT_RUNNER_TEST_RESULTS_DIR}/results_for_{dataset_name}.jsonl"


def ssl_verification_enabled():
    """Check if SSL verification is disabled."""
    return os.environ.get("SSL_VERIFY", "1") == "1"
