# Matchers

<div class='subtitle'>Use matchers for fuzzy and LLM-based checks</div>

Not all agentic behavior can be specified with precise, traditional checking methods. Instead, more often than not, we expect AI models to generalize and thus respond slightly differently to different inputs.

To accommodate this, `testing` includes several different `Matcher` implementations, that allow you to write tests that rely on fuzzy, similarity-based or property-based conditions.

## `IsSimilar`

TODO

## `LambdaMatcher`

TODO

## `IsFactuallyEqual`

Checks for factual equality / entailment of two sentences or words. This can be used to check if two sentences are factually equivalent, or subset/superset of each other.

TODO