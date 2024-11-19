import base64
from invariant_runner.custom_types.invariant_value import InvariantValue
from invariant_runner.scorers.utils.llm import LLM_Classifier
from pytest import approx

def test_contains():
    res = InvariantValue("hello", ["prefix"]).contains("el")
    assert len(res.addresses) == 1 and res.addresses[0] == "prefix:1-3"
    assert not InvariantValue("hello", [""]).contains("\\d")

def test_levenshtein():
    assert InvariantValue("hello").levenshtein("hallo") == approx(0.8)

def test_is_valid_code():
    assert InvariantValue("def hello():\n\treturn 1").is_valid_code("python")

    res = InvariantValue("""a = 2\n2x = a\nc=a""", ["messages.0.content"]).is_valid_code("python")
    assert len(res.addresses) == 1 and res.addresses[0] == "messages.0.content:6-12"
    assert not res

    invalid_json_example = """
    {
        "hello": "world",
        "foo": 'bar',
        "baz": 123
    }
    """

    res = InvariantValue(invalid_json_example, ["messages.0.content"]).is_valid_code("json")
    assert len(res.addresses) == 1 and res.addresses[0] == "messages.0.content:33-54"
    assert not res

    assert InvariantValue("""{"hello": "world"}""").is_valid_code("json")

def test_is_similar():
    res = InvariantValue("hello", ["prefix"]).is_similar("hallo")
    assert len(res.addresses) == 1 and res.addresses[0] == "prefix"
    assert not InvariantValue("banana").is_similar("quantum", 0.9)

def test_moderation():
    res = InvariantValue("hello there\ni want to kill them\nbye", [""]).moderation()
    assert len(res.addresses) == 1
    assert res.addresses[0] == ":11-31"

def test_llm():
    res = InvariantValue("I am feeling great today!").llm("Does the text have positive sentiment?", ["yes", "no"])
    assert res.value == "yes"

    res = InvariantValue("Heute ist ein schöner Tag").llm("Which language is this text in?", ["en", "it", "de", "fr"])
    assert res.value == "de"

def test_extract():
    res = InvariantValue("I like apples and carrots, but I don't like bananas.\nThe only thing better than apples are potatoes and pears.", ["message.0.content"]).extract("fruits")
    assert len(res.value) == 4
    assert res.value[0].value == "apples" and res.value[0].addresses[0] == "message.0.content:7-13"
    assert res.value[1].value == "bananas" and res.value[1].addresses[0] == "message.0.content:44-51"
    assert res.value[2].value == "apples" and res.value[2].addresses[0] == "message.0.content:80-86"
    assert res.value[3].value == "pears" and res.value[3].addresses[0] == "message.0.content:104-109"
    
def test_vision_classifier():
    with open("sample_tests/assets/Group_of_cats_resized.jpg", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    img = InvariantValue(base64_image, [""])
    res = img.llm_vision("What is in the image?", ["cats", "dogs", "birds", "none"])
    assert res.value == "cats"
    res = img.llm_vision("How many cats are in the image?", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    assert res.value == "3"

def test_ocr_detector():
    from invariant_runner.scorers.utils.ocr import OCR_Detector
    # Load test image
    with open("sample_tests/assets/inv_labs.png", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Test case-insensitive detection
    assert InvariantValue(base64_image, [""]).ocr_contains(base64_image, "agents")
    assert InvariantValue(base64_image, [""]).ocr_contains(base64_image, "making", bbox={'x1': 50, 'y1': 10, 'x2': 120, 'y2': 40})
    assert not InvariantValue(base64_image, [""]).ocr_contains(base64_image, "LLM")
