UNCERTAINTY_PHRASES = [
    "i'm not sure", "i am not sure", "i don't know", "i do not know",
    "i cannot", "i can't", "as an ai", "i'm unable to", "i am unable to",
    "unclear", "insufficient information",
]

MIN_ANSWER_LENGTH = 10


def is_low_confidence(answer: str) -> bool:
    """
    Lightweight safety net: catches obviously broken/refused answers
    even when difficulty classification judged the question 'easy'.
    """
    if not answer or len(answer.strip()) < MIN_ANSWER_LENGTH:
        return True

    lowered = answer.lower()
    for phrase in UNCERTAINTY_PHRASES:
        if phrase in lowered:
            return True

    return False