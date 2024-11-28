import ast
import os
import tempfile


def get_code_blocks(file):
    code_blocks = []
    line_before = ""
    with open(file, "r") as f:
        lines = f.readlines()
        code_block = []
        in_code_block = False
        for line in lines:
            if line.startswith("```python"):
                in_code_block = True
            elif line.startswith("```") and in_code_block:
                if in_code_block:
                    code_blocks.append("".join(code_block))
                    code_block = []
                    in_code_block = False
            elif in_code_block:
                code_block.append(line)
            line_before = line
        if code_block:
            code_blocks.append("".join(code_block))

    return code_blocks


def run_snippets(file):
    # get all code blocks from markdown file
    code_blocks = get_code_blocks(file)
    for i, cb in enumerate(code_blocks):
        try:
            # makes sure imports and parsing works
            parsed = ast.parse(cb)
            exec(compile(parsed, filename="<ast>", mode="exec"))
        except Exception as e:
            print("Failed to run code block", i, "in", file)
            print(e)
        # run as pytest
        with tempfile.NamedTemporaryFile("w", suffix=".py") as f:
            f.write(cb)
            f.seek(0)
            print("Running code block", i, "in", file)
            os.system(f"pytest {f.name}")


if __name__ == "__main__":
    run_snippets("Writing_Tests/2_Tests.md")
