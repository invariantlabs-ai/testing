import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from invariant.testing import Trace
import json

def run_python(code):
    import sys 
    from io import StringIO 
    stdout = sys.stdout 
    sys.stdout = StringIO() 
    try: 
        exec(code) 
        output = sys.stdout.getvalue() 
    except Exception as e:
        output = str(e) 
    finally:
        sys.stdout = stdout
    return output

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Run the provided snippet of Python code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to run",
                    },
                },
                "required": ["code"]
            },
        }
    }
]
    
class OpenaiPythonAgent:
    """An openai agent that run Pyhon code fullfilling the user's request then return the result."""
    def __init__(self):
        self.client = openai.OpenAI()
        self.prompt = """
                        You are an assistant that strictly responds with Python code only. 
                        The code should print the result.
                        You always use tool run_python to execute the code that you write to present the results.
                        If the user specifies other programming language in the question, you should respond with "I can only help with Python code."
                    """

    def get_response(self, user_input: str):
        
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_input}
        ]

        while True:
            response = self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o",
                tools=tools,
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                response_message = response_message.to_dict()
                messages.append(response_message)
                # In this demo there's only one tool call in the response
                tool_call = tool_calls[0]
                if tool_call.function.name == "run_python":
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = run_python(function_args["code"])
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": "run_python",
                            "content": str(function_response),
                        }
                    )
            else:
                break
        messages.append(response.choices[0].message.to_dict())
        return messages
    