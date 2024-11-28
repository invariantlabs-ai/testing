## Invariant testing library

### Setup Env Variables 
```bash
export OPENAI_API_KEY=abc
export INVARIANT_API_KEY=def
```

Get the Open AI Key from [here](https://platform.openai.com/settings/organization/api-keys).

Get the Invariant API key by following the steps [here](https://explorer.invariantlabs.ai/docs/). 

### Running sample tests

To run the sample tests, first install the package locally by running `pip install -e .` in the root directory.

Then, you can `invariant test --push sample_tests/` if you want to run with the Invariant runner. 

Else, do `pytest sample_tests -s -vv `. This will not use the Invariant runner but will still allow usage of the context manager.

## Running tests while development 

To run without coverage, do `pytest -s -vv tests/`.

To run with coverage, do `pytest --cov=invariant --cov-report=html -s -vv tests/`.
