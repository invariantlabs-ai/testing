from invariant_runner.scorers.code import is_valid_json, is_valid_python


def test_is_valid_json():
    assert is_valid_json("""{"key": "value"}""")[0]
    assert not is_valid_json("not json")[0]


def test_is_valid_python():
    assert is_valid_python("print('hello')")[0]
    assert not is_valid_python("2 = b")[0]
