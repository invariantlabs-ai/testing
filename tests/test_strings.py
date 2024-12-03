import base64

import pytest
from invariant.scorers.base import approx
from invariant.scorers.strings import *
from invariant.scorers.utils.llm import LLMClassifier, LLMDetector
from invariant.scorers.utils.ocr import OCRDetector
from invariant.utils.packages import is_program_installed

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
    llm_clf = LLMClassifier(
        model="gpt-4o",
        prompt="Does the text have positive sentiment?",
        options=["yes", "no"],
    )
    res = llm_clf.classify(text="I am feeling great today!")
    assert res == "yes"

    llm_clf = LLMClassifier(
        model="gpt-4o",
        prompt="Which language is this text in?",
        options=["en", "it", "de", "fr"],
    )
    res = llm_clf.classify(text="Heute ist ein schöner Tag")
    assert res == "de"


def test_llm_detector():
    text = """I like apples and carrots, but I don't like bananas.\nThe only thing better than apples are potatoes and pears."""
    llm_detector = LLMDetector(model="gpt-4o", predicate_rule="fruits")
    detections = [value for (value, addresses) in llm_detector.detect(text)]
    assert detections[0] == "apples"
    assert detections[1] == "bananas"
    assert detections[2] == "apples"
    assert detections[3] == "pears"


def test_vision_classifier():
    with open("sample_tests/assets/Group_of_cats_resized.jpg", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    llm_clf = LLMClassifier(
        model="gpt-4o-mini",
        prompt="What is in the image?",
        options=["cats", "dogs", "birds", "none"],
        vision=True,
    )
    res = llm_clf.classify_vision(base64_image)
    assert res == "cats"

    llm_clf = LLMClassifier(
        model="gpt-4o",
        prompt="How many cats are in the image?",
        options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        vision=True,
    )
    res = llm_clf.classify_vision(base64_image)
    assert res == "3"


@pytest.mark.skipif(
    not is_program_installed("tesseract"),
    reason="May not have tesseract installed",
)
def test_OCRDetector():
    from PIL import Image
    image = Image.open("sample_tests/assets/inv_labs.png")

    # Test case-insensitive detection
    ocr = OCRDetector()
    assert ocr.contains(image, "agents") == True
    assert (
        ocr.contains(
            image, "making", bbox={"x1": 50, "y1": 10, "x2": 120, "y2": 40}
        )
        == True
    )
