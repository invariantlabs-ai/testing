"""Describes an invariant string in a test."""

from __future__ import annotations

import json
import re
from operator import ge, gt, le, lt, ne
from typing import Any, Optional, Union

from _pytest.python_api import ApproxBase
from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_list import InvariantList
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_value import InvariantValue
from invariant_runner.scorers.code import is_valid_json, is_valid_python
from invariant_runner.scorers.moderation import ModerationAnalyzer
from invariant_runner.scorers.strings import embedding_similarity, levenshtein
from invariant_runner.scorers.utils.llm import LLMClassifier, LLMDetector
from invariant_runner.scorers.utils.ocr import OCRDetector
from invariant_runner.scorers.code import execute


class InvariantString(InvariantValue):
    """Describes an invariant string in a test."""

    def __init__(self, value: str, addresses: list[str] = None):
        if not isinstance(value, str):
            raise TypeError(f"value must be a str, got {type(value)}")
        if addresses is None:
            addresses = []
        super().__init__(value, addresses)

    def _compare(self, other: Union[str, "InvariantString"], operator) -> InvariantBool:
        """Helper function to compare with another string."""
        if isinstance(other, InvariantString):
            other = other.value
        cmp_result = operator(self.value, other)
        return InvariantBool(cmp_result, self.addresses)

    def __eq__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is equal to the given string."""
        if isinstance(other, InvariantString):
            other = other.value
        if isinstance(other, ApproxBase):
            return self.value == other
        return InvariantBool(self.value == other, self.addresses)

    def __ne__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is not equal to the given string."""
        return self._compare(other, ne)

    def __gt__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is greater than the given string."""
        return self._compare(other, gt)

    def __lt__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is less than the given string."""
        return self._compare(other, lt)

    def __ge__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is greater than or equal to the given string."""
        return self._compare(other, ge)

    def __le__(self, other: Union[str, "InvariantString"]) -> InvariantBool:
        """Check if the string is less than or equal to the given string."""
        return self._compare(other, le)

    def __add__(self, other: Union[str, "InvariantString"]) -> "InvariantString":
        """Concatenate the string with another string."""
        if isinstance(other, InvariantString):
            return InvariantString(
                self.value + other.value, self.addresses + other.addresses
            )
        return InvariantString(self.value + other, self.addresses)

    def __radd__(self, other: str) -> "InvariantString":
        """Concatenate another string with this string (reverse operation)."""
        return InvariantString(other + self.value, self.addresses)

    def __str__(self) -> str:
        return f"InvariantString(value={self.value}, addresses={self.addresses})"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self):
        raise NotImplementedError(
            "InvariantString does not support len(). Please use .len() instead."
        )

    def __getitem__(self, key: Any, default: Any = None) -> "InvariantString":
        """Get a substring using integer, slice or string."""
        if isinstance(key, int):
            range = f"{key}-{key+1}"
            return InvariantString(self.value[key], self._concat_addresses([range]))
        elif isinstance(key, str):
            valid_json = self.is_valid_code("json")
            if not valid_json:
                return default
            json_dict = json.loads(self.value)
            # TODO: We can find more precise address here
            return InvariantString(json_dict[key], self.addresses)
        elif isinstance(key, slice):
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else len(self.value)
            range = f"{start}-{stop}"
            return InvariantString(self.value[key], self._concat_addresses([range]))
        raise TypeError("InvariantString indices must be integer, slices or strings")

    def count(self, pattern: str) -> InvariantNumber:
        """Counts the number of occurences of the given regex pattern."""
        new_addresses = []
        for match in re.finditer(pattern, self.value):
            start, end = match.span()
            new_addresses.append(f"{start}-{end}")
        return InvariantNumber(
            len(new_addresses),
            (
                self.addresses
                if len(new_addresses) == 0
                else self._concat_addresses(new_addresses)
            ),
        )

    def len(self):
        """Return the length of the list."""
        return InvariantNumber(len(self.value), self.addresses)

    def __getattr__(self, attr):
        """
        Delegate attribute access to the underlying string.

        Args:
            attr (str): The attribute being accessed.

        Returns:
            Any: Uses InvariantValue.of to return the result.
                 If the result is a string, then an InvariantString is returned with that
                 the result string as the value. If the result is a number, then an InvariantNumber.
        """
        if hasattr(self.value, attr):
            method = getattr(self.value, attr)

            # If the method is callable, wrap it to return an InvariantValue where appropriate
            if callable(method):

                def wrapper(*args, **kwargs):
                    result = method(*args, **kwargs)
                    return InvariantValue.of(result, self.addresses)

                return wrapper
            return method
        raise AttributeError(f"'InvariantString' object has no attribute '{attr}'")

    def _concat_addresses(
        self, other_addresses: list[str] | None, separator: str = ":"
    ) -> list[str]:
        """Concatenate the addresses of two invariant values."""
        if other_addresses is None:
            return self.addresses
        addresses = []
        for old_address in self.addresses:
            # Check if old_address ends with :start-end pattern
            match = re.match(r"^(.*):(\d+)-(\d+)$", old_address)
            assert match is not None
            prefix, start, _ = (
                match.groups()[0],
                int(match.groups()[1]),
                int(match.groups()[2]),
            )
            for new_address in other_addresses:
                new_match = re.match(r"^(\d+)-(\d+)$", new_address)
                assert new_match is not None
                new_start, new_end = (
                    start + int(new_match.groups()[0]),
                    start + int(new_match.groups()[1]),
                )
                addresses.append(prefix + separator + f"{new_start}-{new_end}")
        return addresses

    def moderation(self) -> InvariantBool:
        """Check if the value is moderated."""

        analyzer = ModerationAnalyzer()
        res = analyzer.detect_all(self.value)
        new_addresses = [str(range) for _, range in res]
        return InvariantBool(len(res) > 0, self._concat_addresses(new_addresses))

    def contains(self, pattern: str | InvariantString) -> InvariantBool:
        """Check if the value contains the given pattern."""
        if isinstance(pattern, InvariantString):
            pattern = pattern.value
        new_addresses = []
        for match in re.finditer(pattern, self.value):
            start, end = match.span()
            new_addresses.append(f"{start}-{end}")
        return InvariantBool(
            len(new_addresses) > 0,
            (
                self.addresses
                if len(new_addresses) == 0
                else self._concat_addresses(new_addresses)
            ),
        )

    def __contains__(self, pattern: str | InvariantString) -> InvariantBool:
        """Check if the value contains the given pattern."""
        return self.contains(pattern)

    def is_similar(self, other: str, threshold: float = 0.5) -> InvariantBool:
        """Check if the value is similar to the given string using cosine similarity."""
        if not isinstance(other, str):
            raise ValueError("is_similar() is only supported for string values")
        cmp_result = embedding_similarity(self.value, other) >= threshold
        return InvariantBool(cmp_result, self.addresses)

    def levenshtein(self, other: str) -> InvariantNumber:
        """Check if the value is similar to the given string using the Levenshtein distance."""
        if not isinstance(other, str):
            raise ValueError("levenshtein() is only supported for string values")
        cmp_result = levenshtein(self.value, other)
        return InvariantNumber(cmp_result, self.addresses)

    def is_valid_code(self, lang: str) -> InvariantBool:
        """Check if the value is valid code in the given language."""
        if lang == "python":
            res, new_addresses = is_valid_python(self.value)
            return InvariantBool(res, self._concat_addresses(new_addresses))
        if lang == "json":
            res, new_addresses = is_valid_json(self.value)
            return InvariantBool(res, self._concat_addresses(new_addresses))
        raise ValueError(f"Unsupported language: {lang}")

    def llm(
        self,
        prompt: str,
        options: list[str],
        model: str = "gpt-4o",
        use_cached_result: bool = True,
    ) -> InvariantString:
        """Check if the value is similar to the given string using an LLM.

        Args:
            prompt (str): The prompt to use for the LLM.
            options (list[str]): The options to use for the LLM.
            model (str): The model to use for the LLM.
            use_cached_result (bool): Whether to use a cached result if available.
        """
        llm_clf = LLMClassifier(model=model, prompt=prompt, options=options)
        res = llm_clf.classify(self.value, use_cached_result)
        return InvariantString(res, self.addresses)

    def llm_vision(
        self,
        prompt: str,
        options: list[str],
        model: str = "gpt-4o",
        use_cached_result: bool = True,
    ) -> InvariantString:
        """Check if the value is similar to the given string using an LLM.

        Args:
            prompt (str): The prompt to use for the LLM.
            options (list[str]): The options to use for the LLM.
            model (str): The model to use for the LLM.
            use_cached_result (bool): Whether to use a cached result if available
        """
        llm_clf = LLMClassifier(
            model=model, prompt=prompt, options=options, vision=True
        )
        res = llm_clf.classify_vision(self.value, use_cached_result)
        return InvariantString(res, self.addresses)

    def extract(
        self, predicate: str, model: str = "gpt-4o", use_cached_result: bool = True
    ) -> InvariantList:
        """Extract values from the underlying string using an LLM.

        Args:
            predicate (str): The predicate to use for extraction. This is a rule that the LLM uses to extract
                             values. For example with a predicate "cities in Switzerland", the LLM would extract
                             all cities in Switzerland from the text.
            model (str): The model to use for extraction.
            use_cached_result (bool): Whether to use a cached result if available.
        """
        llm_detector = LLMDetector(model=model, predicate_rule=predicate)
        detections = llm_detector.detect(self.value, use_cached_result)
        values, addresses = [], []
        for substr, r in detections:
            values.append(substr)
            addresses.extend(self._concat_addresses([str(r)]))
        return InvariantList(values, addresses)

    def ocr_contains(
        self,
        text: str,
        case_sensitive: bool = False,
        bbox: Optional[dict] = None,
    ) -> InvariantBool:
        """Check if the value contains the given text using OCR."""

        ocr = OCRDetector()
        res = ocr.contains(self.value, text, case_sensitive, bbox)
        return InvariantBool(res, self.addresses)

    def execute(self, suffix_code: str = "", detect_packages: bool = False) -> InvariantString:
        """Execute the value as Python code and return the standard output as InvariantString.

        Args:
            suffix_code (str): The Python code to append to the value before execution.
            detect_packages (bool): Whether to detect the dependencies of the code.
        """
        res = execute(self.value + "\n" + suffix_code, detect_packages)
        return InvariantString(res, self.addresses)
