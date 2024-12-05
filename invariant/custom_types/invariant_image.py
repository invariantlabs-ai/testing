"""A custom type for an invariant image."""

import base64
import io
from typing import Optional

from PIL import Image

from invariant.custom_types.invariant_bool import InvariantBool
from invariant.custom_types.invariant_string import InvariantString
from invariant.scorers.utils.llm import LLMClassifier
from invariant.scorers.utils.ocr import OCRDetector


class InvariantImage(InvariantString):
    """An invariant image."""

    def __init__(self, value: str, addresses: Optional[list[str]] = None):
        if value.startswith("local_base64_img: "):
            value = value[16:]
        super().__init__(value, addresses)
        image_data = base64.b64decode(value)
        self.image = Image.open(io.BytesIO(image_data))
        assert isinstance(self.image, Image.Image)

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

    def ocr_contains(
        self,
        text: str | InvariantString,
        case_sensitive: bool = False,
        bbox: Optional[dict] = None,
    ) -> InvariantBool:
        """Check if the value contains the given text using OCR."""
        addresses = self.addresses
        if type(text) == InvariantString:
            addresses.extend(text.addresses)
            text = text.value
        res = OCRDetector().contains(self.image, text, case_sensitive, bbox)
        return InvariantBool(res, addresses)

    def ocr_contains_any(
        self,
        texts: list[str | InvariantString],
        case_sensitive: bool = False,
        bbox: Optional[dict] = None,
    ) -> InvariantBool:
        for text in texts:
            if self.ocr_contains(text, case_sensitive, bbox).value:
                return InvariantBool(True, self.addresses)
        return InvariantBool(False, self.addresses)

    def ocr_contains_all(
        self,
        texts: list[str | InvariantString],
        case_sensitive: bool = False,
        bbox: Optional[dict] = None,
    ) -> InvariantBool:
        for text in texts:
            if not self.ocr_contains(text, case_sensitive, bbox).value:
                return InvariantBool(False, self.addresses)
        return InvariantBool(True, self.addresses)
