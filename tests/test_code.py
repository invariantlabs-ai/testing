from invariant_runner.scorers.code import *


def test_is_valid_json():
    assert is_valid_json("""{"key": "value"}""")
    assert not is_valid_json("not json")


def test_is_valid_python():
    assert is_valid_python("print('hello')")
    assert not is_valid_python("2 = b")
