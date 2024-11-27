import json
import subprocess
import tempfile
from typing import Tuple

import openai
from pydantic import BaseModel

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
    except Exception:
        return False, None


def execute(text: str, detect_packages: bool = False) -> str:
    class Dependencies(BaseModel):
        dependencies: list[str]

    """Executes a string of Python code and returns the standard output.
    Optionally, this function can also detect the dependencies of the code using an LLM and append them as a header to the code.
    The code runs inside of a docker container and uses uv package manager to quickly install the dependencies.

    Args:
        text (str): The Python code to execute.
        detect_packages (bool): Whether to detect the dependencies of the code.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        with open(file_path, "w") as f:
            f.write(text)

    if detect_packages:
        prompt = f"""Extract the dependencies necessary to run the following python code:\n\n{
            text}"""
        client = openai.OpenAI()
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format=Dependencies,
        )
        dependencies = response.choices[0].message.parsed
        with open(file_path, "r") as f:
            script_content = f.read()

        new_content = (
            f"# /// script\n# dependencies = {json.dumps(dependencies.dependencies)}\n# ///\n"
            + script_content
        )
        with open(file_path, "w") as f:
            f.write(new_content)

    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-v",
        f"{file_path}:/usr/src/app/script.py:ro",
        "-w",
        "/usr/src/app",
        "ghcr.io/astral-sh/uv:0.5.4-python3.12-bookworm",
        "uv",
        "run",
        "script.py",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout
