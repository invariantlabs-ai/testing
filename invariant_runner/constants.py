"""Constants for the Invariant Test Runner."""
from enum import Enum

INVARIANT_RUNNER_TEST_RESULTS_DIR = "/tmp/invariant_test_runner"
INVARIANT_AP_KEY_ENV_VAR = "INVARIANT_API_KEY"
INVARIANT_TEST_RUNNER_CONFIG_ENV_VAR = "INVARIANT_TEST_RUNNER_CONFIG"

class Similaritymetrics(Enum):
    LEVENSHTEIN = "levenshtein"
    EMBEDDING = "embedding"