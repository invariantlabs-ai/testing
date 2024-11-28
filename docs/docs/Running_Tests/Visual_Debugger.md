# Visual Debugging

<div class='subtitle'>Use Explorer to view test failures and debug your agent.</div>

When building test suites with `testing`, you can use the [Invariant Explorer](https://explorer.invariantlabs.ai/docs/) to visually inspect the results of your tests, which can greatly improve your debugging workflow. 

To do so, just run your tests with the `--push` flag to send the results to the Explorer:

```bash
invariant test --push
```

The Explorer can render long-form agent traces in a more readable format, and it can also display test result and localized assertions down to the character level.

![Explorer](assets/explorer.png)

<center>Viewing test results in Explorer</center>

## Getting Started With Visual Debugging

### 1. Sign Up for Explorer

To use Explorer, first make sure to sign up for an account according to [the instructions in the Explorer documentation](https://explorer.invariantlabs.ai/docs/) and obtain your personal API key.

Next, store your Invariant API as a environment variable in your current shell:

```bash
export INVARIANT_API_KEY=inv-...
```

### 2. Run and Push Test Results

Then, you can run your tests with the `--push` flag to send the results to the Explorer:

```bash
invariant test --push
```

This will show the regular test output but also pushes all created agent traces to Explorer, which you can then view on completion in your browser. Each test run will result in a separate trace dataset in Explorer, allowing you to track test results over time.

Agent traces pushed with `testing` contain special metadata to highlight overall test success or failure, as well as to localize all assertions within the trace. This applies both to successful and failed assertions, allowing you to better debug and understand your agent and test conditions.