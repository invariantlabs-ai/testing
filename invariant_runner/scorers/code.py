import ast
import json
from typing import Tuple

from invariant_runner.custom_types.addresses import Range


def is_valid_json(text: str) -> Tuple[bool, int | None]:
    """Check if a string is valid JSON."""
    try:
        json.loads(text)
        return True, None
    except json.JSONDecodeError as e:
        return False, [Range.from_line(text, e.lineno - 1).to_address()]


def is_valid_python(text: str) -> Tuple[bool, int | None]:
    """Check if a string is valid Python code."""
    try:
        compile(text, "<string>", "exec")
        return True, None
    except SyntaxError as e:
        return False, [Range.from_line(text, e.lineno - 1).to_address()]
    except:
        return False, None
