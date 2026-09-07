import json

with open('evaluation/results/raw_results.json') as f:
    data = json.load(f)

scored = [e for e in data if 'always_cheap' in e and 'quality_score' in e['always_cheap']]
print(f"Fully scored questions: {len(scored)}")
print("IDs:", sorted([e["id"] for e in scored]))