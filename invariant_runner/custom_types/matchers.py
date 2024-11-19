"""Defines the expect functions."""

from typing import Any
from invariant_runner.constants import SimilarityMetrics
from invariant_runner.scorers.strings import *

class Matcher:
    """Base class for all matchers."""

    def matches(self, actual_value: Any) -> bool:
        """This is the method that subclasses should implement."""
        raise NotImplementedError("Subclasses should implement this method.")


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
    """ Matcher for checking if a string is similar to expected string by check if the simliarty score reaches the threshold"""

    metric_to_scorer_mapping = {
        SimilarityMetrics.LEVENSHTEIN: levenshtein,
        SimilarityMetrics.EMBEDDING: embedding_similarity
    }

    def __init__(self, expected_value: str, threshold: float, actual_metric: SimilarityMetrics = SimilarityMetrics.LEVENSHTEIN):
        self.expected_value = expected_value
        self.threshold = threshold
        self.actual_metric = actual_metric
    
    def matches(self, actual_value: str):
        if not isinstance(actual_value, str):
            raise TypeError("CompareSimilarity matcher only works with strings")
        if self.actual_metric not in self.metric_to_scorer_mapping:
            raise ValueError(f"Unsupported metric {self.actual_metric}")
        
        similar_score = self.metric_to_scorer_mapping[self.actual_metric](actual_value, self.expected_value)
        return similar_score >= self.threshold
