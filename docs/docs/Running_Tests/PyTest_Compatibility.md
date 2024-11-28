# `pytest` Compatibility

<div class='subtitle'>Use <code>testing</code> as part of your existing <code>pytest</code> test suite.</div>

`testing` is built to seamlessly integrate with [`pytest`](https://docs.pytest.org/en/stable/). In fact, all test discovery and execution is done through `pytest` itself, which means the `invariant test` command can be considered a `pytest` equivalent entry point.

## The `invariant test` CLI

`invariant test` is a lightweight wrapper of the original `pytest` CLI. It is designed to be a drop-in replacement for `pytest` in your existing test suite.

On top of the standard `pytest` arguments, `invariant test` supports the following extra arguments to enable [pushing to Explorer](./Visual_Debugger.md).

**Extra Arguments**

```bash
--dataset_name DATASET_NAME (optional)
```

The name of the dataset to be used to associate the test trace data and
results. This name will be used to derive a fresh dataset name on each run
(e.g. myproject-1732007573)

```bash
--push (optional)
```

Flag to indicate whether to [push data to Explorer](./Visual_Debugger.md). If set to true,
the `INVARIANT_API_KEY` environment variable must be set. Visit the [Explorer Documentation](https://explorer.invariantlabs.ai/docs) to learn how to obtain your own API key.

### Example Commands

**Run all tests in a directory:**
```bash
invariant test tests/
```

**Run all tests in a file:**
```bash
invariant test tests/test_my_module.py
```

**Run a specific test:**
```bash
invariant test tests/test_my_module.py::test_my_function
```

**Run all tests in a directory and push data to Explorer:**
```bash
invariant test tests/ --push
```

**Run all tests in a file and push data to Explorer (dataset name is `myproject`):**
```bash
invariant test tests/test_my_module.py --push --dataset_name myproject
```

Apart from these basic examples, you can use any other `pytest` arguments as well. For more information, refer to the [pytest documentation](https://docs.pytest.org/en/stable/usage.html#specifying-tests-selecting-tests).

<br/>

## Running with `pytest` directly

If you prefer to run `pytest` directly, you can do so by running the following command:

```bash
pytest tests/
```

This will run all tests, including `testing` agent test cases. Note however, that when running `pytest` directly, the `--push` and `--dataset_name` arguments are not supported and you won't be able to push test results to Explorer.

For more information on `pytest`, refer to the [pytest documentation](https://docs.pytest.org/en/stable/).