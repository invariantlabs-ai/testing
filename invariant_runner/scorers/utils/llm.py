import json
import openai


PROMPT_TEMPLATE = """Your goal is to classify the text provided by the user using the following classification rule.
{prompt}

Call the function `option_selector` with the best of the following options as the argument: {options}
"""


class LLM_Classifier:

    def __init__(self, model: str, prompt: str, options: list[str]):
        self.model = model
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


    def classify(self, text: str) -> str:
        prompt = self.prompt.format(text=text)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
            tools=self.tools,
            tool_choice="required",
        )
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments).get("best_option", "none")
