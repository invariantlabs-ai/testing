# content of tests/test_weather.py
# for pytest parametrization
from pytest import mark

from invariant_runner.testing import Trace, assert_equals, assert_true


def test_weather():
    # create a Trace object from your agent trajectory
    trace = Trace(
        trace=[
            {"role": "user", "content": "What is the weather like in Paris?"},
            {"role": "agent", "content": "The weather in London is 75°F and sunny."},
        ]
    )

    # make assertions about the agent's behavior
    with trace.as_context():
        locations = trace.messages()[-1]["content"].extract("locations")

        assert_equals(
            1, locations.len(), "The agent should respond about one location only"
        )
        assert_equals("Paris", locations[0], "The agent should respond about Paris")


# some other unti testing functions that make sense in this context


def test_non_us_countr():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


def test_us_countr():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


def test_refusal():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


def test_off_topic():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


def test_invalid_request():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


def test_alignment():
    city = "Paris"

    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )


@mark.parametrize(
    "city",
    [
        "Paris",
        "London",
        "New York",
        "San Francisco",
        "Los Angeles",
        "Tokyo",
        "Sydney",
    ],
)
def test_city(city: str):
    trace = Trace(
        trace=[{"role": "user", "content": f"What is the weather like in {city}?"}]
    )

    with trace.as_context():
        assert_true(
            trace.messages()[-1]["content"].contains(city),
        )
