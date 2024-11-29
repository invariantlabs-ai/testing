"""Utility functions for the invariant runner."""
import os
import shutil

from invariant.constants import (
    INVARIANT_RUNNER_TEST_RESULTS_DIR,
    INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR,
)


def get_test_results_directory_path(dataset_name: str) -> str:
    """Get the directory path for the test results."""
    return f"{INVARIANT_RUNNER_TEST_RESULTS_DIR}/results_for_{dataset_name}"


def ssl_verification_enabled():
    """Check if SSL verification is disabled."""
    return os.environ.get("SSL_VERIFY", "1") == "1"


def terminal_width():
    """Get the terminal width."""

    if INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR in os.environ:
        return int(os.environ[INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR])
    return shutil.get_terminal_size().columns
