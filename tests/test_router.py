from src.router.fallback import is_low_confidence


def test_empty_answer_triggers_fallback():
    assert is_low_confidence("") is True


def test_very_short_answer_triggers_fallback():
    assert is_low_confidence("Yes.") is True


def test_hedge_phrase_triggers_fallback():
    assert is_low_confidence("I'm not sure, but maybe it's Paris?") is True


def test_refusal_triggers_fallback():
    assert is_low_confidence("I cannot answer that question.") is True


def test_confident_full_answer_does_not_trigger_fallback():
    answer = "The capital of France is Paris, a city located on the Seine river."
    assert is_low_confidence(answer) is False


def test_technical_answer_does_not_trigger_fallback():
    answer = (
        "The Byzantine Generals Problem describes a scenario where distributed "
        "nodes must reach consensus despite the presence of malicious actors."
    )
    assert is_low_confidence(answer) is False