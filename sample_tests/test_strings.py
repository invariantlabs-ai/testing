import pytest
from invariant_runner.scorers.strings import *
from invariant_runner.scorers.base import approx
from invariant_runner.scorers.utils.llm import LLM_Classifier


def test_levenshtein():
    # Test empty strings
    assert levenshtein("", "") == pytest.approx(1.0)
    assert levenshtein("", "a") == pytest.approx(0.0)
    assert levenshtein("a", "") == pytest.approx(0.0)

    # Test identical strings
    assert levenshtein("hello", "hello") == pytest.approx(1.0)
    assert levenshtein("test", "test") == pytest.approx(1.0)

    # Test different strings
    assert levenshtein("kitten", "sitting") == pytest.approx(0.571, abs=0.001)
    assert levenshtein("hello", "world") == pytest.approx(0.2, abs=0.001)
    
    # Test special characters
    assert levenshtein("hello!", "hello") == pytest.approx(0.833, abs=0.001)
    assert levenshtein("test123", "test") == pytest.approx(0.571, abs=0.001)
    assert levenshtein("@#$", "@#$") == pytest.approx(1.0)


def test_embedding_similarity():
    assert approx("hello") == "hi"
    assert "banana" != approx("quantum")
    assert approx("happy") == "joyful"


def test_contains():
    assert contains("hello", "he")
    assert contains("hello abc123", "\\d+")
    assert not contains("hello", "quantum")


def test_llm():
    llm_clf = LLM_Classifier(model="gpt-4o", prompt="Does the text have positive sentiment?", options=["yes", "no"])
    res = llm_clf.classify(text="I am feeling great today!")
    assert res == "yes"

    llm_clf = LLM_Classifier(model="gpt-4o", prompt="Which language is this text in?", options=["en", "it", "de", "fr"])
    res = llm_clf.classify(text="Heute ist ein schöner Tag")
    assert res == "de"



        
