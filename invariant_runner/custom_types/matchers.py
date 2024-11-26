"""Defines the expect functions."""

from typing import Any

from invariant_runner.scorers.strings import embedding_similarity, levenshtein


class Matcher:
    """Base class for all matchers."""

    def matches(self, actual_value: Any) -> bool:
        """This is the method that subclasses should implement."""
        raise NotImplementedError("Subclasses should implement this method.")


class LambdaMatcher(Matcher):
    """Matcher for checking if a lambda function returns True."""

    def __init__(self, lambda_function):
        self.lambda_function = lambda_function

    def matches(self, actual_value: Any) -> bool:
        """Check if the lambda function returns True for actual_value."""
        return self.lambda_function(actual_value)

    def __str__(self):
        return f"LambdaMatcher({self.lambda_function})"

    def __repr__(self):
        return str(self)


class HasSubstring(Matcher):
    """Matcher for checking if a string contains a substring."""

    def __init__(self, substring: str):
        self.substring = substring

    def matches(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, str):
            raise TypeError("HasSubstring matcher only works with strings.")
        return self.substring in actual_value

    def __str__(self):
        return f"HasSubstring({self.substring})"

    def __repr__(self):
        return str(self)


class IsSimilar(Matcher):
    """A Matcher for checking if a string is similar to an expected string by checking if the similary score reaches a given threshold."""

    LEVENSHTEIN = "levenshtein"
    EMBEDDING = "embedding"

    metric_to_scorer_mapping = {
        LEVENSHTEIN: levenshtein,
        EMBEDDING: embedding_similarity,
    }

    def __init__(
        self,
        expected_value: str,
        threshold: float,
        actual_metric: str = LEVENSHTEIN,
    ):
        self.expected_value = expected_value
        self.threshold = threshold
        self.actual_metric = actual_metric

    def matches(self, actual_value: str):
        if not isinstance(actual_value, str):
            raise TypeError("CompareSimilarity matcher only works with strings")
        if self.actual_metric not in self.metric_to_scorer_mapping:
            raise ValueError(f"Unsupported metric {self.actual_metric}")

        similar_score = self.metric_to_scorer_mapping[self.actual_metric](
            actual_value, self.expected_value
        )
        return similar_score >= self.threshold
