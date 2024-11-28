"""Defines the expect functions."""

from enum import StrEnum
from typing import Any

from invariant.scorers.strings import embedding_similarity, levenshtein
from invariant.scorers.utils.llm import LLMClassifier


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


class IsFactuallyEqual(Matcher):
    """Matcher for checking if the output is close to expected using llm"""

    class Agreement(StrEnum):
        SUPER_STRICT_AGGREMENT = "super strict aggrement"
        STRICT_AGGREMENT = "strict aggrement"
        FUZZY_AGGREMENT = "fuzzy aggrement"

    levels_to_score_mapping = {
        Agreement.FUZZY_AGGREMENT: 1,
        Agreement.STRICT_AGGREMENT: 2,
        Agreement.SUPER_STRICT_AGGREMENT: 3,
    }

    def __init__(
        self,
        expected_value: str,
        question: str,
        level: Agreement = Agreement.STRICT_AGGREMENT,
    ):
        assert (
            level in self.levels_to_score_mapping.keys()
        ), f"Invalid scoring level {level}. Must be one of {self.levels_to_score_mapping.keys()}"

        self.expected_value = expected_value
        self.question = question
        self.level = level

    def matches(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, str):
            raise TypeError("is factually equivalent matcher only works with strings")
        prompt = """You are comparing a submitted answer to an expert answer on a given question.
                    Compare the factual content of the submitted answer with the expert answer. Ignore any differences in style, grammar, or punctuation.
                    The submitted answer may either be a subset or superset of the expert answer, or it may conflict with it. Determine which case applies. Answer the question by selecting one of the following options:
                    (0) There is a disagreement between the submitted answer and the expert answer.
                    (1) The submitted answer is a subset of the expert answer and is fully consistent with it.
                    (2) The submitted answer is a superset of the expert answer and is fully consistent with it.
                    (3) The answers differ, but these differences don't matter from the perspective of factuality.
                    (4) The submitted answer contains all the same details as the expert answer.
                 """
        text = f"""Here is the data:
                    [Question]: {self.question},
                    [Expert]: {self.expected_value},
                    [Submission]: {actual_value},
                """
        llm_clf = LLMClassifier(
            model="gpt-4o", prompt=prompt, options=["0", "1", "2", "3", "4"]
        )
        res_score = llm_clf.classify(text=text)
        print(f"result: {res_score}")

        try:
            res_score_number = int(res_score)
        except ValueError:
            raise ValueError(f"llm returned invalid result {res_score}")

        return res_score_number >= self.levels_to_score_mapping[self.level]
