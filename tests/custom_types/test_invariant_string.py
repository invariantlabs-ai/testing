"""Test cases for the InvariantString class."""

import base64

import pytest
from invariant_runner.custom_types.invariant_bool import InvariantBool
from invariant_runner.custom_types.invariant_list import InvariantList
from invariant_runner.custom_types.invariant_number import InvariantNumber
from invariant_runner.custom_types.invariant_string import InvariantString
from pytest import approx


def test_invariant_string_initialization():
    """Test initialization of InvariantString."""
    string = InvariantString("Hello", ["addr1"])
    assert string.value == "Hello"
    assert string.addresses == ["addr1:0-5"]

    # Test default addresses
    string = InvariantString("World")
    assert string.addresses == []
    assert string.len() == 5
    assert string.upper() == "WORLD"
    assert string.lower() == "world"

    # Test invalid value type
    with pytest.raises(TypeError, match="value must be a str"):
        InvariantString(123)

    # Test invalid addresses type
    with pytest.raises(TypeError, match="addresses must be a list of strings"):
        InvariantString("Hello", [1, 2, 3])


@pytest.mark.parametrize(
    "value1, value2, expected",
    [
        (InvariantString("Hello"), "Hello", True),
        (InvariantString("Hello"), "World", False),
        (InvariantString("Hello"), InvariantString("Hello"), True),
        (InvariantString("Hello"), InvariantString("World"), False),
    ],
)
def test_invariant_string_equality(value1, value2, expected):
    """Test equality of InvariantString objects."""
    result = value1 == value2
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value1, value2, expected",
    [
        (InvariantString("Hello"), "Hello", False),
        (InvariantString("Hello"), "World", True),
        (InvariantString("Hello"), InvariantString("Hello"), False),
        (InvariantString("Hello"), InvariantString("World"), True),
    ],
)
def test_invariant_string_inequality(value1, value2, expected):
    """Test inequality of InvariantString objects."""
    result = value1 != value2
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value, substring, expected",
    [
        (InvariantString("Hello World"), "World", True),
        (InvariantString("Hello World"), "world", False),  # Case-sensitive
        (InvariantString("Hello"), "Hell", True),
        (InvariantString("Hello"), "o", True),
        (InvariantString("Hello"), "Goodbye", False),
    ],
)
def test_invariant_string_contains(value, substring, expected):
    """Test the contains method of InvariantString."""
    result = value.contains(substring)
    assert isinstance(result, InvariantBool)
    assert result.value == expected


@pytest.mark.parametrize(
    "value1, value2, expected_value, expected_addresses",
    [
        (InvariantString("Hello"), "World", "HelloWorld", []),
        (
            InvariantString("Hello", ["addr1"]),
            InvariantString("World", ["addr2"]),
            "HelloWorld",
            ["addr1:0-5", "addr2:0-5"],
        ),
        ("World", InvariantString("Hello", ["addr1"]), "WorldHello", ["addr1:0-5"]),
    ],
)
def test_invariant_string_concatenation(
    value1, value2, expected_value, expected_addresses
):
    """Test the concatenation of InvariantString objects."""
    result = value1 + value2
    assert isinstance(result, InvariantString)
    assert result.value == expected_value
    assert result.addresses == expected_addresses


def test_invariant_string_str_and_repr():
    """Test string representation of InvariantString."""
    string = InvariantString("Hello", ["addr1"])
    assert str(string) == "InvariantString(value=Hello, addresses=['addr1:0-5'])"
    assert repr(string) == "InvariantString(value=Hello, addresses=['addr1:0-5'])"


def test_contains():
    """Test the contains transformer of InvariantString."""
    # res = InvariantString("hello", ["prefix"]).contains("el")
    # assert len(res.addresses) == 1 and res.addresses[0] == "prefix:1-3"
    assert not InvariantString("hello", [""]).contains("\\d")


def test_levenshtein():
    """Test the levenshtein transformer of InvariantString."""
    res = InvariantString("hello").levenshtein("hallo")
    assert isinstance(res, InvariantNumber)
    assert res == approx(0.8)


def test_is_valid_code():
    """Test the is_valid_code transformer of InvariantString."""
    assert InvariantString("def hello():\n\treturn 1").is_valid_code("python")

    res = InvariantString(
        """a = 2\n2x = a\nc=a""", ["messages.0.content"]
    ).is_valid_code("python")
    assert isinstance(res, InvariantBool)
    assert len(res.addresses) == 1 and res.addresses[0] == "messages.0.content:6-12"
    assert not res

    invalid_json_example = """
    {
        "hello": "world",
        "foo": 'bar',
        "baz": 123
    }
    """

    res = InvariantString(invalid_json_example, ["messages.0.content"]).is_valid_code(
        "json"
    )
    assert isinstance(res, InvariantBool)
    assert len(res.addresses) == 1 and res.addresses[0] == "messages.0.content:33-54"
    assert not res

    assert InvariantString("""{"hello": "world"}""").is_valid_code("json")


def test_is_similar():
    """Test the is_similar transformer of InvariantString."""
    res = InvariantString("hello", ["prefix"]).is_similar("hallo")
    assert isinstance(res, InvariantBool)
    assert len(res.addresses) == 1 and res.addresses[0] == "prefix:0-5"
    assert not InvariantString("banana").is_similar("quantum", 0.9)


def test_moderation():
    """Test the moderation transformer of InvariantString."""
    res = InvariantString("hello there\ni want to kill them\nbye", [""]).moderation()
    assert isinstance(res, InvariantBool)
    assert len(res.addresses) == 1
    assert res.addresses[0] == ":11-31"


def test_llm():
    """Test the llm transformer of InvariantString."""
    res = InvariantString("I am feeling great today!").llm(
        "Does the text have positive sentiment?", ["yes", "no"]
    )
    assert isinstance(res, InvariantString) and res.value == "yes"
    res = InvariantString("Heute ist ein schöner Tag").llm(
        "Which language is this text in?", ["en", "it", "de", "fr"]
    )
    assert isinstance(res, InvariantString) and res.value == "de"


def test_extract():
    """Test the extract transformer of InvariantString."""
    res = InvariantString(
        "I like apples and carrots, but I don't like bananas.\nThe only thing better than apples are potatoes and pears.",
        ["message.0.content"],
    ).extract("fruits")
    assert isinstance(res, InvariantList)
    assert len(res.value) == 4
    assert res.value[0] == "apples" and res.addresses[0] == "message.0.content:7-13"
    assert res.value[1] == "bananas" and res.addresses[1] == "message.0.content:44-51"
    assert res.value[2] == "apples" and res.addresses[2] == "message.0.content:80-86"
    assert res.value[3] == "pears" and res.addresses[3] == "message.0.content:104-109"


def test_vision_classifier():
    with open("sample_tests/assets/Group_of_cats_resized.jpg", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    img = InvariantString(base64_image, [""])
    res = img.llm_vision("What is in the image?", ["cats", "dogs", "birds", "none"])
    assert isinstance(res, InvariantString) and res.value == "cats"
    res = img.llm_vision(
        "How many cats are in the image?",
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    )
    assert isinstance(res, InvariantString) and res.value == "3"


def test_ocr_detector():
    # Load test image
    from invariant_runner.scorers.utils.ocr import OCR_Detector

    if not OCR_Detector.check_tesseract_installed():
        pytest.skip("Tesseract is not installed")
    with open("sample_tests/assets/inv_labs.png", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Test case-insensitive detection
    assert InvariantString(base64_image, [""]).ocr_contains(base64_image, "agents")
    assert InvariantString(base64_image, [""]).ocr_contains(
        base64_image, "making", bbox={"x1": 50, "y1": 10, "x2": 120, "y2": 40}
    )
    assert not InvariantString(base64_image, [""]).ocr_contains(base64_image, "LLM")
