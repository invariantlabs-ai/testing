"""Utility functions for using language models."""

import json
import logging
from typing import Tuple

import openai
from invariant_runner.cache.cache_manager import CacheManager
from invariant_runner.custom_types.addresses import Range
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from pydantic import BaseModel

PROMPT_TEMPLATE = """Your goal is to classify the text provided by the user
using the following classification rule.
{prompt}

Call the function `option_selector` with the best of the following options as the argument: {options}
"""

PROMPT_TEMPLATE_VISION = """Your goal is to classify the image provided by the user
using the following classification rule.
{prompt}

Call the function `option_selector` with the best of the following options as the argument: {options}
"""

LLM_DETECTOR_PROMPT_TEMPLATE = """Your goal is to extract parts of the text the match the
predicate rule. Here is one example:

Predicate rule: 
cities in Switzerland

Text:
1| I arrived to Zurich last week by train from Munich.
2| I am going to visit Geneva next week, and Bern the week after.
3| After Bern, I am going to Paris, France.

Detections:
[("1", "Zurich"), ("2", "Geneva"), ("2", "Bern"), ("3", "Bern")]

Use the following predicate rule to find the detections in the next user message:
{predicate_rule}
"""

CACHE_DIRECTORY_LLM_CLASSIFIER = ".invariant/cache/llm_classifier"
CACHE_DIRECTORY_LLM_DETECTOR = ".invariant/cache/llm_detector"
CACHE_TIMEOUT = 3600
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClassifier:
    """Class to classify using a language model."""

    def __init__(self, model: str, prompt: str, options: list[str], vision: bool = False, default_ttl: int = 3600):
        """
        Args:
            model (str): The language model to use.
            prompt (str): The prompt to use for the classification.
            options (list[str]): The options to choose from when classifying.
            vision (bool): Whether to classify images instead of text.
            default_ttl (int): The default time-to-live for the cache.
        """
        self.model = model
        if vision:
            self.prompt = PROMPT_TEMPLATE_VISION.format(
                prompt=prompt, options=",".join(options))
        else:
            self.prompt = PROMPT_TEMPLATE.format(
                prompt=prompt, options=",".join(options))
        self.options = options
        self.client = openai.OpenAI()
        self.tools = [{
            "type": "function",
            "function": {
                "name": "option_selector",
                "description": "Selects the best option from the list of options",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "best_option": {
                            "type": "string",
                        },
                    },
                }
            }
        }]
        self.cache_manager = CacheManager(
            CACHE_DIRECTORY_LLM_CLASSIFIER, expiry=default_ttl)

    def _make_completions_create_request(self, request_data: dict, use_cached_result: bool) -> ChatCompletion:
        """Make a request to the language model."""
        if not use_cached_result:
            return self.client.chat.completions.create(**request_data)

        cache_key = self.cache_manager.get_cache_key(request_data)
        response = self.cache_manager.get(cache_key)
        if response:
            logger.info("Using cached response for request.")
            return response

        logger.warning("Cache miss. Making request to OpenAI.")
        # Make the actual request
        response = self.client.chat.completions.create(**request_data)

        # Store the response in the cache with an expiry
        self.cache_manager.set(cache_key, response)

        return response

    def classify_vision(self, base64_image: str, use_cached_result: bool = True) -> str:
        """Classify an image using the language model.

        Args:
            base64_image (str): The base64-encoded image to classify.
            use_cached_result (bool): Whether to use a cached result if available.
        """
        response = self._make_completions_create_request({
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": [{"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}
            ],
            "tools": self.tools,
            "tool_choice": "required",
        }, use_cached_result)
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments).get("best_option", "none")

    def classify(self, text: str, use_cached_result: bool = True) -> str:
        """Classify a text using the language model.

        Args:
            text (str): The text to classify.
            use_cached_result (bool): Whether to use a cached result if available.
        """
        response = self._make_completions_create_request({
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text}
            ],
            "tools": self.tools,
            "tool_choice": "required",
        }, use_cached_result)
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments).get("best_option", "none")


class DetectionPair(BaseModel):
    """Model for a detection pair."""
    line: int
    substring: str


class Detections(BaseModel):
    """Model for a list of detections."""
    detections: list[DetectionPair]


class LLMDetector:
    """Class to detect using a language model."""

    def __init__(self, model: str, predicate_rule: str, default_ttl: int = 3600):
        """
        Args:
            model (str): The language model to use.
            predicate_rule (str): The predicate rule to use for detection. The predicate to use
                                  for extraction. This is a rule that the LLM uses to extract values.
                                  For example with a predicate "cities in Switzerland", the LLM would
                                  extract all cities in Switzerland from the text.
            default_ttl (int): The default time-to-live for the cache.
        """
        self.model = model
        self.predicate_rule = predicate_rule
        self.client = openai.OpenAI()
        self.cache_manager = CacheManager(
            CACHE_DIRECTORY_LLM_DETECTOR, expiry=default_ttl)

    def _insert_lines(self, text: str) -> str:
        return "\n".join(f"{i}| {line}" for i, line in enumerate(text.split("\n"), 1))

    def _to_serializable(self, response):
        """Convert a response object to a JSON-compatible dictionary."""
        return response.model_dump()

    def _from_serializable(self, cached_response):
        """Convert a cached JSON-compatible dictionary back to a response object."""
        return ParsedChatCompletion[Detections].model_validate(cached_response)

    def _make_completions_parse_request(self, request_data: dict, use_cached_result: bool):
        """Make a request to the language model."""
        if not use_cached_result:
            return self.client.beta.chat.completions.parse(**request_data)

        cache_key = self.cache_manager.get_cache_key(request_data)
        response = self.cache_manager.get(cache_key)
        if response:
            logger.info("Using cached response for request.")
            return self._from_serializable(response)

        logger.warning("Cache miss. Making request to OpenAI.")
        # Make the actual request
        response = self.client.beta.chat.completions.parse(**request_data)

        # Store the response in a serializable format
        serializable_response = self._to_serializable(response)
        self.cache_manager.set(cache_key, serializable_response)

        return response

    def detect(self, text: str, use_cached_result: bool = True) -> list[Tuple[str, Range]]:
        """Detect parts of the text that match the predicate rule.

        Args:
            text (str): The text to detect on.
            use_cached_result (bool): Whether to use a cached result if available.
        """
        formatted_text = self._insert_lines(text)
        prompt = LLM_DETECTOR_PROMPT_TEMPLATE.format(
            predicate_rule=self.predicate_rule)
        response = self._make_completions_parse_request({
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": formatted_text}
            ],
            "response_format": Detections,
        }, use_cached_result)
        detections = response.choices[0].message.parsed
        return [(det.substring, Range.from_line(text, det.line-1, exact_match=det.substring)) for det in detections.detections]
