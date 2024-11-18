from invariant_runner.scorers.moderation import ModerationAnalyzer


def test_moderation():
    mod_analyzer = ModerationAnalyzer()

    res = mod_analyzer.detect_all("I want to kill them!")
    assert any(result.entity == "violence" for result in res)

    res = mod_analyzer.detect_all("I am very happy!")
    assert len(res) == 0
