from invariant_runner.custom_types.assertions import (
    assert_that,
)
from invariant_runner.custom_types.matchers import IsSimilar
from invariant_runner.custom_types.trace import Trace
from invariant_runner.manager import Manager
from invariant_runner.constants import SimilarityMetrics

def test_is_similar_levenshtein():
    # not passing metrics parameter, default using Levenshtein metric or pass SimilarityMetrics.LEVENSHTEIN
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    with Manager(trace) as _:
        # test case: expected value is longer than actual value
        assert_that(trace.messages()[0]["content"], IsSimilar("hello where",0.5))
        assert_that(trace.messages()[0]["content"], IsSimilar("Hello there Hello there Hello there",0.4,SimilarityMetrics.LEVENSHTEIN))
        # test case: expected value is shorter than actual value, empty
        assert_that(trace.messages()[0]["content"], IsSimilar("hello",0.8))
        assert_that(trace.messages()[0]["content"], IsSimilar("",0.5,SimilarityMetrics.LEVENSHTEIN))
        assert_that(trace.messages()[0]["content"], IsSimilar("there",0.5))
        # test case: expected value is the same length as actual value
        assert_that(trace.messages()[0]["content"], IsSimilar("hello aaaaa", 0.3,SimilarityMetrics.LEVENSHTEIN))
        assert_that(trace.messages()[0]["content"], IsSimilar("hello THERe",0.9,SimilarityMetrics.LEVENSHTEIN))
        assert_that(trace.messages()[0]["content"], IsSimilar("iiiii THERE",0.5))

def test_is_similar_embedding():
    # pass SimilarityMetrics.EMBEDDING as parameter
    trace = Trace(trace=[{"role": "user", "content": "Hello there"}])
    with Manager(trace) as _:
        # test case: similar meaning
        assert_that(trace.messages()[0]["content"], IsSimilar("hi there",0.8, SimilarityMetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], IsSimilar("how are you",0.4, SimilarityMetrics.EMBEDDING))
        # test case: unrelated meaning but similar spell
        assert_that(trace.messages()[0]["content"], IsSimilar("hello where",0.5, SimilarityMetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], IsSimilar("hello three",0.5, SimilarityMetrics.EMBEDDING))
        # test case: unrelated meaning and different spell
        assert_that(trace.messages()[0]["content"], IsSimilar("where are you",0.5, SimilarityMetrics.EMBEDDING))
        assert_that(trace.messages()[0]["content"], IsSimilar("I am fine",0.5, SimilarityMetrics.EMBEDDING))