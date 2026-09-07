import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.cheap_model import call_cheap_model
from src.models.expensive_model import call_expensive_model
from src.router.classifier import route_question

DATA_PATH = "data/test_questions.json"
RESULTS_PATH = "evaluation/results/raw_results.json"


def load_questions():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def load_existing_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, "r") as f:
            return json.load(f)
    return []


def save_results(results):
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)


def already_done(results, question_id):
    """Check if this question already has all 3 strategy results recorded."""
    entry = next((r for r in results if r["id"] == question_id), None)
    if entry is None:
        return False
    return all(k in entry for k in ["always_cheap", "always_expensive", "router"])


def run_batch(start_idx: int, end_idx: int):
    """
    Runs questions from start_idx to end_idx (inclusive, 1-indexed by question 'id')
    through all three strategies, saving results incrementally after each question.
    """
    questions = load_questions()
    results = load_existing_results()

    batch = [q for q in questions if start_idx <= q["id"] <= end_idx]
    print(f"Running batch: questions {start_idx}-{end_idx} ({len(batch)} questions)")

    for q in batch:
        if already_done(results, q["id"]):
            print(f"  [skip] Q{q['id']} already completed")
            continue

        print(f"  [running] Q{q['id']}: {q['question'][:60]}...")

        entry = {
            "id": q["id"],
            "question": q["question"],
            "expected_difficulty": q["expected_difficulty"],
        }

        try:
            entry["always_cheap"] = call_cheap_model(q["question"])
            time.sleep(0.5)  # small pause to be gentle on rate limits

            entry["always_expensive"] = call_expensive_model(q["question"])
            time.sleep(0.5)

            entry["router"] = route_question(q["question"])
            time.sleep(0.5)

        except Exception as e:
            print(f"  [ERROR] Q{q['id']} failed: {e}")
            entry["error"] = str(e)

        # Remove any old partial entry for this question, then add the new one
        results = [r for r in results if r["id"] != q["id"]]
        results.append(entry)
        save_results(results)

    print(f"Batch complete. Total results saved: {len(results)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python evaluation/run_eval.py <start_id> <end_id>")
        print("Example: python evaluation/run_eval.py 1 30")
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    run_batch(start, end)