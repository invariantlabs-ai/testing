# Integrate Your Agent

<div class='subtitle'>Get your agent ready for testing</div>

Invariant `testing` relies on a very simple yet powerful trace format as the common denominator for testing agents. 

This trace format is a list of dictionaries, where each dictionary represents a message in the conversation. Each message has a `role` key that specifies the role of the speaker (e.g., `user` or `agent`) and a `content` key that contains the message content.

```json
{"role": "user", "content": "Hello there"},
{"role": "assistant", "content": "Hello there", "tool_calls": [
    {
        "type": "function",
        "function": {
            "name": "greet",
            "arguments": {
                "name": "there"
            }
        }
    }
]},
{"role": "user", "content": "I need help with something."},
```