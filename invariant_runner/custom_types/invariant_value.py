"""Describes an invariant value in a test."""
from __future__ import annotations
import re
# pylint: disable=import-outside-toplevel
from typing import Any, Optional
from invariant_runner.scorers.strings import *
from invariant_runner.scorers.code import *
from invariant_runner.scorers.utils.llm import LLM_Classifier, LLM_Detector

from _pytest.python_api import ApproxBase

class InvariantValue:
    """Describes an invariant value in a test."""

    def __init__(self, value: Any, addresses: list[str] = None):
        if addresses is not None and not all(
            isinstance(addr, str) for addr in addresses
        ):
            raise TypeError("addresses must be a list of strings")
        self.value = value
        self.addresses = addresses if addresses is not None else []

        if isinstance(self.value, str) and self.addresses is None:
            for i, a in enumerate(self.addresses):
                if ":" not in a:
                    self.addresses[i] = a + ":0-" + str(len(self.value))

    @staticmethod
    def of(value: Any, address: list[str]):
        """Create an Invariant type object from a value and a list of addresses."""
        from .invariant_bool import InvariantBool
        from .invariant_dict import InvariantDict
        from .invariant_list import InvariantList
        from .invariant_number import InvariantNumber
        from .invariant_string import InvariantString

        if isinstance(value, list):
            assert isinstance(
                address, list
            ), "InvariantValue.of requires a list of adresses for list values"
            return InvariantList(value, address)
        elif isinstance(value, dict):
            assert isinstance(address, list), (
                "InvariantValue.of requires a list of adresses for dict values, got "
                + str(address)
                + " "
                + str(type(address))
            )
            return InvariantDict(value, address)
        elif isinstance(value, (int, float)):
            return InvariantNumber(value, address)
        elif isinstance(value, str):
            return InvariantString(value, address)
        elif isinstance(value, bool):
            return InvariantBool(value, address)
        return InvariantValue(value, address)

    def equals(self, value: Any) -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value is equal to the given value."""
        from .invariant_bool import InvariantBool

        cmp_result = self.value == value
        return InvariantBool(cmp_result, self.addresses)

    def matches(self, matcher: "Matcher") -> "InvariantBool":  # type: ignore # noqa: F821
        """Check if the value matches the given matcher."""
        from .invariant_bool import InvariantBool

        cmp_result = matcher.matches(self.value)
        return InvariantBool(cmp_result, self.addresses)

    def __str__(self):
        return str(self.value) + " at " + " -> ".join(self.addresses)

    def __repr__(self):
        return str(self)

    def __bool__(self) -> bool:
        """Convert the invariant value to a boolean."""
        return bool(self.value)

    def __float__(self) -> float:
        """Convert the invariant value to a float."""
        return float(self.value)

    def __eq__(self, other: Any) -> bool:
        """Check if the invariant value is equal to the given value."""
        if isinstance(other, ApproxBase):
            return self.value == other
        return self.value == other

    def _concat_addresses(self, other_addresses: list[str] | None, separator: str = ":") -> list[str]:
        """Concatenate the addresses of two invariant values."""
        if other_addresses is None:
            return self.addresses
        addresses = []
        for old_address in self.addresses:
            for new_address in other_addresses:
                addresses.append(old_address + separator + new_address)
        return addresses

    def moderation(self) -> InvariantValue:
        """Check if the value is moderated."""
        from invariant_runner.scorers.moderation import ModerationAnalyzer
        analyzer = ModerationAnalyzer()
        res = analyzer.detect_all(self.value)
        new_addresses = [str(range) for _, range in res]
        return InvariantValue(len(res) > 0, self._concat_addresses(new_addresses))

    def contains(self, pattern: str) -> InvariantValue:
        """Check if the value contains the given pattern."""
        if type(self.value) != str:
            raise ValueError("contains() is only supported for string values")
        new_addresses = []
        for match in re.finditer(pattern, self.value):
            start, end = match.span()
            new_addresses.append(f"{start}-{end}")
        return InvariantValue(len(new_addresses) > 0, self._concat_addresses(new_addresses))

    def is_similar(self, other: str, threshold: float = 0.5) -> InvariantValue:
        """Check if the value is similar to the given string using cosine similarity."""
        if type(self.value) != str or type(other) != str:
            raise ValueError("is_similar() is only supported for string values")
        cmp_result = embedding_similarity(self.value, other) >= threshold
        return InvariantValue(cmp_result, self.addresses)

    def levenshtein(self, other: str) -> InvariantValue:
        """Check if the value is similar to the given string using the Levenshtein distance."""
        if type(self.value) != str or type(other) != str:
            raise ValueError("levenshtein() is only supported for string values")
        cmp_result = levenshtein(self.value, other)
        return InvariantValue(cmp_result, self.addresses)

    def is_valid_code(self, lang: str) -> InvariantValue:
        """Check if the value is valid code in the given language."""
        if type(self.value) != str:
            raise ValueError("is_valid_code() is only supported for string values")
        if lang == "python":
            res, new_addresses = is_valid_python(self.value)
            return InvariantValue(res, self._concat_addresses(new_addresses))
        elif lang == "json":
            res, new_addresses = is_valid_json(self.value)
            return InvariantValue(res, self._concat_addresses(new_addresses))
        else:
            raise ValueError(f"Unsupported language: {lang}")

    def llm(self, prompt: str, options: list[str], model: str = "gpt-4o") -> InvariantValue:
        """Check if the value is similar to the given string using an LLM."""
        llm_clf = LLM_Classifier(model=model, prompt=prompt, options=options)
        res = llm_clf.classify(self.value)
        return InvariantValue(res, self.addresses)

    def llm_vision(self, prompt: str, options: list[str], model: str = "gpt-4o") -> InvariantValue:
        """Check if the value is similar to the given string using an LLM."""
        llm_clf = LLM_Classifier(model=model, prompt=prompt, options=options, vision=True)
        res = llm_clf.classify_vision(self.value)
        return InvariantValue(res, self.addresses)

    def extract(self, predicate: str, model: str = "gpt-4o") -> list[InvariantValue]:
        """Extract a value from the value using an LLM."""
        llm_detector = LLM_Detector(model=model, predicate_rule=predicate)
        detections = llm_detector.detect(self.value)
        ret = []
        for substr, range in detections:
            ret.append(InvariantValue(substr, self._concat_addresses([str(range)])))
        return InvariantValue(ret, self.addresses)
 
    def ocr_contains(self, base64_image: str, text: str, case_sensitive: bool = False, bbox: Optional[dict] = None) -> InvariantValue:
        """Check if the value contains the given text using OCR."""
        from invariant_runner.scorers.utils.ocr import OCR_Detector
        ocr = OCR_Detector()
        res = ocr.contains(base64_image, text, case_sensitive, bbox)
        return InvariantValue(res, self.addresses)
