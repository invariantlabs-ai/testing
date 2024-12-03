import invariant.testing as it

trace_id = "9fb90e2a-66dd-49d3-9561-9b6cae7e2082" 
trace = it.Trace.from_explorer(trace_id)

def test_flow():
    with trace.as_context():
       
        idx = 0 
        # TODO -- should be more elegant
        screenshot_checks = [
            lambda x: x.ocr_contains("Untitled 1 - LibreOffice Calc"), # open LibreOffice  
            lambda x: x.llm_vision("Is cell D15 highlighted?", ["Yes", "No"]) == 'Yes', # select the right cell
            lambda x: x.ocr_contains("asdf"), # type "asdf" in the cell
            lambda x: x.ocr_contains("Save as"), # open save dialog
            lambda x: x.ocr_contains("test.csv") and not x.ocr_contains("test.csvUntitled 1"), # save the file
        ]
        
        for tc, tcr in trace.tool_pairs():
            if tc.get('name') == 'screenshot':
                result = screenshot_checks[idx](tcr)
                if result:
                    idx += 1
        it.assert_true(idx == len(screenshot_checks), "All screenshot checks passed")
       
        
def test_not_cheating():
    with trace.as_context():
        bash_calls = trace.tool_calls({"name":"bash"})
        #TODO is there a better way to do this?
        for bash_call in bash_calls:
            command = bash_call.get("function").get("arguments").get("command", "")
            it.assert_false(command.contains("echo"), "No echo commands in bash calls")

def test_no_unnecessary_installs():
    with trace.as_context():
        bash_calls = trace.tool_calls({"name":"bash"})
        for bash_call in bash_calls:
            command = bash_call.get("function").get("arguments").get("command", "")
            #it.expect_false(command.contains("apt") and command.contains("install"), "No need to install anything") # TODO this does not do what it should
            it.expect_false(command.contains("apt") & command.contains("install"), "No need to install anything") # TODO this works though