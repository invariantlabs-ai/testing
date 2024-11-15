import ast
import json


def is_valid_json(text: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(text)
        return True
    except:
        return False


def is_valid_python(text: str) -> bool:
    """Check if a string is valid Python code."""
    try:
        compile(text, "<string>", "exec")
        return True
    except:
        return False
