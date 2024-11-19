"""Defines the expect functions."""

from typing import Any
from invariant_runner.constants import Similaritymetrics
from invariant_runner.scorers.strings import *

class Matcher:
    """Base class for all matchers."""

    def matches(self, actual_value: Any) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")


class has_substring(Matcher):
    """Matcher for checking if a string contains a substring."""

    def __init__(self, substring: str):
        self.substring = substring

    def matches(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, str):
            raise TypeError("has_substring matcher only works with strings.")
        return self.substring in actual_value

    def __str__(self):
        return f"has_substring({self.substring})"

    def __repr__(self):
        return str(self)
    
class is_similar(Matcher):
    """ Matcher for checking if a string is similar to expected string by check if the simliarty score reaches the threshold"""
    def __init__(self, expected_value: str, threshold: float, actual_metric: Similaritymetrics = Similaritymetrics.LEVENSHTEIN):
        self.expected_value = expected_value
        self.threshold = threshold
        self.actual_metric = actual_metric
        self.metrics = {
            Similaritymetrics.LEVENSHTEIN: levenshtein,
            Similaritymetrics.EMBEDDING: embedding_similarity
        }
    
    def matches(self, actual_value: str):
        if not isinstance(actual_value, str):
            raise TypeError("CompareSimilarity matcher only works with strings")
        if self.actual_metric not in self.metrics:
            raise ValueError(f"Unsupported metric {self.actual_metric}")
        
        similar_score = self.metrics[self.actual_metric](actual_value, self.expected_value)
        return similar_score >= self.threshold