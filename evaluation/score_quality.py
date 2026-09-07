import json
import time
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from src.config import GROQ_API_KEY, CHEAP_MODEL_NAME

# Use the CHEAP model as judge instead — separates judge from the model being evaluated,
# avoids self-grading bias, and reduces load on the already-rate-limited expensive model.
judge_client = Groq(api_key=GROQ_API_KEY)
JUDGE_MODEL = CHEAP_MODEL_NAME

RESULTS_PATH = "evaluation/results/raw_results.json"

JUDGE_PROMPT = (
    "You are a strict, skeptical grader evaluating an AI assistant's answer.\n\n"
    "Question: {question}\n\n"
    "Answer: {answer}\n\n"
    "Grade critically. Look specifically for: factual errors, missing key points, "
    "vagueness, or claims that sound confident but are wrong. Most answers have "
    "SOME flaw — do not default to a perfect score.\n\n"
    "First, in one sentence, state the biggest flaw in this answer (or 'none' if truly flawless).\n"
    "Then on a new line write: Score: X\n"
    "Where X is 1-5:\n"
    "1 = wrong or irrelevant\n"
    "2 = significant errors or major gaps\n"
    "3 = correct but noticeably incomplete or vague\n"
    "4 = correct and complete, with only minor room for improvement\n"
    "5 = correct, complete, precise, nothing meaningful to add"
)


def judge_answer(question: str, answer: str, max_retries=3) -> int | None:
    if not answer or not answer.strip():
        return 1

    prompt = JUDGE_PROMPT.format(question=question, answer=answer)

    for attempt in range(max_retries):
        try:
            response = judge_client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300,
            )
            content = response.choices[0].message.content.strip()
            reasoning = getattr(response.choices[0].message, "reasoning", "") or ""
            source_text = content if content else reasoning

            match = re.search(r"Score:\s*([1-5])", source_text)
            if not match:
                match = re.search(r"\b([1-5])\b", source_text)
            return int(match.group(1)) if match else 3

        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"    Rate limited on attempt {attempt+1}")
                if attempt < max_retries - 1:
                    time.sleep(15 * (attempt + 1))
            else:
                raise

    return None  # signal: could not score, do NOT fake it



def score_all():
    with open(RESULTS_PATH, "r") as f:
        results = json.load(f)

    for entry in results:
        if "error" in entry:
            continue

        for strategy in ["always_cheap", "always_expensive", "router"]:
            if strategy not in entry:
                continue
            if "quality_score" in entry[strategy]:
                continue

            answer = entry[strategy].get("answer", "")
            score = judge_answer(entry["question"], answer)

            if score is None:
                print(f"Q{entry['id']} [{strategy}] -> SKIPPED (rate limited, will retry later)")
                with open(RESULTS_PATH, "w") as f:
                    json.dump(results, f, indent=2)
                print("\nDaily quota likely exhausted. Stopping run — resume later with the same command.")
                return

            entry[strategy]["quality_score"] = score
            print(f"Q{entry['id']} [{strategy}] -> quality {score}")
            time.sleep(1)

        with open(RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)

    print("Scoring complete.")