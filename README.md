## Invariant testing library

### Setup Env Variables 
```bash
export OPENAI_API_KEY=abc
export INVARIANT_API_KEY=def
```

Get the Open AI Key from [here](https://platform.openai.com/settings/organization/api-keys).

Get the Invariant API key by following the steps [here](https://explorer.invariantlabs.ai/docs/). 

### Running tests

To run the sample tests, do `python3 invariant_runner/runner.py -s -vv --push sample_tests/` if you want to run with the Invariant runner. 

Else, do `pytest sample_tests -s -vv `. This will not use the Invariant runner but will still allow usage of the context manager.
