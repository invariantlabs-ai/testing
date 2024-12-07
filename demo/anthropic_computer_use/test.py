import invariant.testing as it
import invariant.testing.functional as F

#trace = it.TraceFactory.from_explorer("9fb90e2a-66dd-49d3-9561-9b6cae7e2082") # failure
trace = it.TraceFactory.from_explorer("7aa6ff9e-06f9-4437-b278-a8b539770a4a") # success

def test_flow():
    with trace.as_context():
        steps = [
            lambda x: x['content'].ocr_contains("LibreOffice Calc"), # open LibreOffice  
            lambda x: x['content'].llm_vision("Is cell D15 highlighted?", ["Yes", "No"]) == 'Yes', # select the right cell
            lambda x: x['content'].llm_vision("Does cell D15 contain asdf?", ["Yes", "No"]) == 'Yes', # enter the right text
            lambda x: x['content'].llm_vision("Is the save as dialog open?", ["Yes", "No"]) == 'Yes', # open save dialog
            lambda x: x['content'].llm_vision("Is the file name in the save as dialog /tmp/test.csv with no superfluous bits appended?", ["Yes", "No"]) == 'Yes', # ensure the file name is correct
        ]
        screenshots = trace.messages(role='tool', data_type='image')
        it.assert_true(F.check_order(steps, screenshots), "Necessary steps are performed in order")

def test_output_correct():
    with trace.as_context():
        cat_stmts = trace.tool_calls({"name":"bash", "arguments": {"command": "cat /tmp/test.csv"}})
        has_output = F.len(cat_stmts) > 0
        it.expect_true(has_output, "result is checked")
        if has_output:
            cat_stmt = cat_stmts[-1]
            output = trace.tool_outputs({"tool_id": cat_stmt['tool_id']})[-1]
            import pandas as pd
            from io import StringIO
            csv_content = output.get("content").get("output")
            it.expect_true(csv_content.contains("asdf"), "output contains the right text")
            df = pd.read_csv(StringIO(csv_content.value))
            it.expect_true(df.iloc[13, 3] == "asdf", "output contains the right text")
            it.expect_true(df.shape == (14, 4), "output contains the right text")
            df.iloc[13, 3] = float('nan')
            it.expect_true(all(df.isna()), "all other cells are empty")

def test_not_cheating():
    with trace.as_context():
        bash_calls = trace.tool_calls({"name":"bash"})
        for bash_call in bash_calls:
            command = bash_call.get("function").get("arguments").get("command", "")
            it.assert_false(command.contains("echo"), "No echo commands in bash calls")

def test_no_unnecessary_installs():
    with trace.as_context():
        bash_calls = trace.tool_calls({"name":"bash"})
        for bash_call in bash_calls:
            command = bash_call.get("function").get("arguments").get("command", "")
            it.expect_false(command.contains("apt") & command.contains("install"), "No need to install anything")