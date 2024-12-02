import json
from pathlib import Path
import requests
import invariant.testing as it

jwt_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGdzBJMnRITUk5cGxzdklJaHVuV1FJUU1fY3ZEZnVZVEhrS0k1OTQ1ZXZBIn0.eyJleHAiOjE3MzMwNjU0MTQsImlhdCI6MTczMzA2NTExNCwiYXV0aF90aW1lIjoxNzMzMDU3MTQxLCJqdGkiOiIzNjM3NjhmNS0yNDA4LTQzYjMtOWJmMi05Njg4NTU5OGYxOTYiLCJpc3MiOiJodHRwczovL2F1dGguaW52YXJpYW50bGFicy5haS9yZWFsbXMvaW52YXJpYW50LXB1YmxpYyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJmNjZiNDVjMy03ZWJjLTRlMmEtYmQ1Ny0wMzFhMTg4MzgzOGEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJpbnZhcmlhbnQtZXhwbG9yZXIiLCJzZXNzaW9uX3N0YXRlIjoiODJhZGNiNGItZmVjYy00MGJmLThmMTEtZjU3ODgwZmQ0MDgzIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2V4cGxvcmVyLmludmFyaWFudGxhYnMuYWkiLCJodHRwczovL3ByZXZpZXctZXhwbG9yZXIuaW52YXJpYW50bGFicy5haSJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJkZWZhdWx0LXJvbGVzLWludmFyaWFudC1wdWJsaWMiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJzaWQiOiI4MmFkY2I0Yi1mZWNjLTQwYmYtOGYxMS1mNTc4ODBmZDQwODMiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJNYXJjIEZpc2NoZXIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ2aWVoemV1ZyIsImdpdmVuX25hbWUiOiJNYXJjIiwiZmFtaWx5X25hbWUiOiJGaXNjaGVyIiwiZW1haWwiOiJtYWlsQG1hcmNmaXNjaGVyLmF0In0.gcEWb6WxZlpRtllotcejOMuGUd10cLICmC_CX3v0LvNPUca0fENLTVbYCKR5aIeR6lGo6xSmDfYylcFf2TnKM8cwlF8K95x17WQ5cYgc6LVKGKA6zVa3ILekDC2vkI_C_wmYobxmaWfzwN5Pnq4gkxIY2fHTxdw-d_bSD1HOKxNeu8M76e4OAoux1tXkaN7wPdyKPNpuNi3vZUkaIHjiPk-PE9JN_PxBQuHe7bOsxOThZH6v-ZcLqcS5hNgv7A7C4fhL2dmSQdpbHc08XaY5x4kzcKqolwOiZdewbV2273dPpZkklByZ9EUvqhywLF7_8ANM1GAohX7EftcUDWPLUQ"

def get_trace(trace_id: str) -> list[dict]:
    response = requests.get(
        f"https://explorer.invariantlabs.ai/api/v1/trace/{trace_id}?annotated=false",
        headers={"accept": "application/json", "Authorization": f"Bearer {jwt_token}"},
        verify=False,
    )
    messages = response.json()["messages"]
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, str) and content.startswith("local_img_link:"):
            img = get_image(content)
            msg["content"] = img
    return messages


def get_image(local_img_path: str) -> str:
    import base64
    
    # Extract components from path
    path_parts = local_img_path.split('/')
    dataset_id = path_parts[-3]
    trace_id = path_parts[-2]
    image_id = path_parts[-1].split('.')[0]

    # Make request to get image
    response = requests.get(
        f"https://explorer.invariantlabs.ai/api/v1/trace/image/{dataset_id}/{trace_id}/{image_id}",
        headers={"accept": "application/json", "Authorization": f"Bearer {jwt_token}"},
        verify=False
    )
    return base64.b64encode(response.content).decode("utf-8")

trace_id = "9fb90e2a-66dd-49d3-9561-9b6cae7e2082" 
path = Path(__file__).parent.joinpath(f"{trace_id}.json")
if path.exists():
    with open(path, 'r') as f:
        trace = json.load(f)
else:
    trace = get_trace(trace_id)
    json.dump(trace, open(path, 'w'))
trace = it.Trace(trace=trace)


def test_flow():
    with trace.as_context():
       
        idx = 0 
        screenshot_checks = [
            lambda x: x.ocr_contains("Untitled 1 - LibreOffice Calc"), # open LibreOffice  
            lambda x: x.llm_vision("Is cell D15 highlighted?", ["Yes", "No"]), # select the right cell
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
        for bash_call in bash_calls:
            it.assert_true("echo" not in bash_call.get("command"), "No echo commands in bash calls")