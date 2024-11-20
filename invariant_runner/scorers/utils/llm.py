import json
import openai
from pydantic import BaseModel
from invariant_runner.custom_types.addresses import Range
from typing import Tuple


PROMPT_TEMPLATE = """Your goal is to classify the text provided by the user using the following classification rule.
{prompt}

Call the function `option_selector` with the best of the following options as the argument: {options}
"""

PROMPT_TEMPLATE_VISION = """Your goal is to classify the image provided by the user using the following classification rule.
{prompt}

Call the function `option_selector` with the best of the following options as the argument: {options}
"""

LLM_DETECTOR_PROMPT_TEMPLATE = """Your goal is to extract parts of the text the match the predicate rule. Here is one example:

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

class LLM_Classifier:

    def __init__(self, model: str, prompt: str, options: list[str], vision: bool = False):
        self.model = model
        if vision:
            self.prompt = PROMPT_TEMPLATE_VISION.format(prompt=prompt, options=",".join(options))
        else:
            self.prompt = PROMPT_TEMPLATE.format(prompt=prompt, options=",".join(options))
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

    def classify_vision(self, base64_image: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt}, 
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
            ],
            tools=self.tools,
            tool_choice="required",
        )
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments).get("best_option", "none")
        
    def classify(self, text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.prompt}, {"role": "user", "content": text}],
            tools=self.tools,
            tool_choice="required",
        )
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments).get("best_option", "none")


class DetectionPair(BaseModel):
    line: int
    substring: str


class Detections(BaseModel):
    detections: list[DetectionPair]


class LLM_Detector:

    def __init__(self, model: str, predicate_rule: str):
        self.model = model
        self.predicate_rule = predicate_rule
        self.client = openai.OpenAI()

    def _insert_lines(self, text: str) -> str:
        return "\n".join(f"{i}| {line}" for i, line in enumerate(text.split("\n"), 1))

    def detect(self, text: str) -> list[Tuple[str, Range]]:
        formatted_text = self._insert_lines(text)
        prompt = LLM_DETECTOR_PROMPT_TEMPLATE.format(predicate_rule=self.predicate_rule)
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": formatted_text}],
            response_format=Detections,
        )
        detections = response.choices[0].message.parsed
        return [(det.substring, Range.from_line(text, det.line-1, exact_match=det.substring)) for det in detections.detections]
