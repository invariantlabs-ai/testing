from .python_agent import OpenaiPythonAgent
from invariant.testing import Trace, assert_true, assert_equals
from unittest.mock import MagicMock

# This is a test that the agent should execute valid python code and get result for a question about fibonacci series
def test_python_question():
    input = "Calculate fibonacci series for 10 in python"
    python_agent = OpenaiPythonAgent()
    response = python_agent.get_response(input)
    trace = Trace.from_openai(response)
    with trace.as_context():
        run_python_tool_call = trace.tool_calls(name="run_python")
        assert_true(len(run_python_tool_call) == 1)
        assert_true(run_python_tool_call[0]["function"]["arguments"]["code"].is_valid_code("python"))
        assert_true("34" in trace.messages(-1)["content"])

# This is a test that mock the agent respond with Java code
def test_python_question_invalid():
    input = "Calculate fibonacci series for 10"
    python_agent = OpenaiPythonAgent()
    mock_invalid_response = [
        {
            "role":"system",
            "content":"\n                    You are an assistant that strictly responds with Python code only. \n                    The code should print the result.\n                    You always use tool run_python to execute the code that you write to present the results.\n                    If the user specifies other programming language in the question, you should respond with \"I can only help with Python code.\"\n                    "
        },
        {
            "role":"user",
            "content":"Calculate fibonacci series for 10"
        },
        {
            "content":"None",
            "refusal":"None",
            "role":"assistant",
            "tool_calls":[
                {
                    "id":"call_GMx1WYM7sN0BGY1ISCk05zez",
                    "function":{
                    "arguments":"{\"code\":\"public class Fibonacci { public static void main(String[] args) { for (int n = 10, a = 0, b = 1, i = 0; i < n; i++, b = a + (a = b)) System.out.print(a + " "); } }\"}",
                    "name":"run_python"
                    },
                    "type":"function"
                }
            ]
        }
    ]
    python_agent.get_response = MagicMock(return_value=mock_invalid_response)
    response = python_agent.get_response(input)
    trace = Trace.from_openai(response)
    with trace.as_context():
        run_python_tool_call = trace.tool_calls(name="run_python")
        assert_true(len(run_python_tool_call) == 1)
        assert_true(not run_python_tool_call[0]["function"]["arguments"]["code"].is_valid_code("python"))

#  This is a test that the request specifies another programming language Java
#  The agent should respond with "I can only help with Python code."
def test_java_question():
    input = "How to calculate fibonacci series in Java?"
    python_agent = OpenaiPythonAgent()
    response = python_agent.get_response(input)
    trace = Trace.from_openai(response)
    with trace.as_context():
        run_python_tool_call = trace.tool_calls(name="run_python")
        assert_true(len(run_python_tool_call) == 0)
        assert_equals("I can only help with Python code.", trace.messages(-1)["content"])
