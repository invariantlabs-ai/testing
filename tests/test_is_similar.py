from invariant_runner.custom_types.assertions import (
    assert_that,
)
from invariant_runner.custom_types.matchers import is_similar
from invariant_runner.custom_types.trace import Trace
from invariant_runner.manager import Manager
from invariant_runner.constants import Similaritymetrics

def test_is_similar_levenshtein():
    # not passing metrics parameter, default using Levenshtein metric or pass Similaritymetrics.LEVENSHTEIN
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    with Manager(trace) as _:
        # test case: expected value is longer than actual value
        assert_that(trace.messages()[0]["content"], is_similar("hello where",0.5))
        assert_that(trace.messages()[0]["content"], is_similar("Hello there Hello there Hello there",0.4))
        # test case: expected value is shorter than actual value, empty
        assert_that(trace.messages()[0]["content"], is_similar("hello",0.8))
        assert_that(trace.messages()[0]["content"], is_similar("",0.5))
        assert_that(trace.messages()[0]["content"], is_similar("there",0.5))
        # test case: expected value is the same length as actual value
        assert_that(trace.messages()[0]["content"], is_similar("hello aaaaa", 0.3))
        assert_that(trace.messages()[0]["content"], is_similar("hello THERe",0.9))
        assert_that(trace.messages()[0]["content"], is_similar("iiiii THERE",0.5))

def test_is_similar_embedding():
    # pass Similaritymetrics.EMBEDDING as parameter
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    with Manager(trace) as _:
        # test case: similar meaning
        assert_that(trace.messages()[0]["content"], is_similar("hi there",0.8, Similaritymetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], is_similar("how are you",0.4, Similaritymetrics.EMBEDDING))
        # test case: unrelated meaning but similar spell
        assert_that(trace.messages()[0]["content"], is_similar("hello where",0.5, Similaritymetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], is_similar("hello three",0.5, Similaritymetrics.EMBEDDING))
        # test case: unrelated meaning and different spell
        assert_that(trace.messages()[0]["content"], is_similar("where are you",0.5, Similaritymetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], is_similar("I am fine",0.5, Similaritymetrics.EMBEDDING))