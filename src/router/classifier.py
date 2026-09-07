import re
from src.models.cheap_model import client as cheap_client, call_cheap_model
from src.models.expensive_model import call_expensive_model
from src.router.fallback import is_low_confidence
from src.config import CHEAP_MODEL_NAME, PRICING, DIFFICULTY_THRESHOLD

DIFFICULTY_PROMPT_TEMPLATE = (
    "Rate the difficulty of the following question on a scale from 1 to 5:\n"
    "1 = trivial factual recall (e.g. 'What is the capital of France?')\n"
    "2 = simple, single-step reasoning or common knowledge\n"
    "3 = requires some domain knowledge or multi-step reasoning\n"
    "4 = requires specialized/expert knowledge or careful multi-step reasoning\n"
    "5 = requires deep expert knowledge, precise technical detail, or complex multi-part reasoning\n\n"
    "Respond with ONLY the number, nothing else.\n\n"
    "Question: {question}"
)


def classify_difficulty(question: str) -> dict:
    """
    Short, cheap call asking the model to rate question difficulty
    WITHOUT answering it. Kept low-cost since output is just one number.
    """
    prompt = DIFFICULTY_PROMPT_TEMPLATE.format(question=question)

    response = cheap_client.chat.completions.create(
        model=CHEAP_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()
    reasoning = getattr(response.choices[0].message, "reasoning", "") or ""

    
    source_text = raw if raw else reasoning
    match = re.search(r"\b([1-5])\b", source_text)
    difficulty = int(match.group(1)) if match else 3

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    price = PRICING[CHEAP_MODEL_NAME]
    cost = (input_tokens / 1000) * price["input"] + (output_tokens / 1000) * price["output"]

    return {
        "difficulty": difficulty,
        "cost_usd": round(cost, 6),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def route_question(question: str) -> dict:
    """
    Classify-then-route design:
    - Judge difficulty FIRST with a short, cheap call (no full answer generated yet)
    - Easy questions -> cheap model answers
    - Hard questions -> expensive model answers directly (cheap model is skipped entirely)
    - A lightweight safety net still checks the cheap model's answer quality
      and escalates if it looks unreliable, even when difficulty seemed low
    """
    classification = classify_difficulty(question)
    difficulty = classification["difficulty"]
    classification_cost = classification["cost_usd"]

    if difficulty <= DIFFICULTY_THRESHOLD:
        cheap_result = call_cheap_model(question)

        if not is_low_confidence(cheap_result["answer"]):
            return {
                **cheap_result,
                "routed_to": "cheap",
                "fallback_triggered": False,
                "difficulty_score": difficulty,
                "classification_cost_usd": classification_cost,
                "total_cost_usd": round(cheap_result["cost_usd"] + classification_cost, 6),
            }

        # Cheap model's answer looked unreliable despite low predicted difficulty
        expensive_result = call_expensive_model(question)
        return {
            **expensive_result,
            "routed_to": "expensive",
            "fallback_triggered": True,
            "difficulty_score": difficulty,
            "classification_cost_usd": classification_cost,
            "cheap_model_attempt": cheap_result,
            "total_cost_usd": round(
                expensive_result["cost_usd"] + cheap_result["cost_usd"] + classification_cost, 6
            ),
        }

    # Difficulty judged high enough to skip the cheap model entirely
    expensive_result = call_expensive_model(question)
    return {
        **expensive_result,
        "routed_to": "expensive",
        "fallback_triggered": False,
        "difficulty_score": difficulty,
        "classification_cost_usd": classification_cost,
        "total_cost_usd": round(expensive_result["cost_usd"] + classification_cost, 6),
    }