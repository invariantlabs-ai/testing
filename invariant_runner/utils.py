"""Utility functions for the invariant runner."""

import os

from invariant_runner.constants import (
    INVARIANT_RUNNER_TEST_RESULTS_DIR,
    INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR)


def get_test_results_file_path(dataset_name: str) -> str:
    """Get the file path for the test results."""
    return f"{INVARIANT_RUNNER_TEST_RESULTS_DIR}/results_for_{dataset_name}.jsonl"


def ssl_verification_enabled():
    """Check if SSL verification is disabled."""
    return os.environ.get("SSL_VERIFY", "1") == "1"


def terminal_width():
    """Get the terminal width."""
    import os
    import shutil

    if INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR in os.environ:
        return int(os.environ[INVARIANT_TEST_RUNNER_TERMINAL_WIDTH_ENV_VAR])
    else:
        return shutil.get_terminal_size().columns
