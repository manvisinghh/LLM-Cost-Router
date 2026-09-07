import json

with open("evaluation/results/raw_results.json") as f:
    data = json.load(f)

routed_cheap = 0
routed_expensive = 0
fallback_count = 0

for entry in data:
    if "router" not in entry or "quality_score" not in entry["router"]:
        continue
    r = entry["router"]
    if r["routed_to"] == "cheap":
        routed_cheap += 1
    else:
        routed_expensive += 1
    if r.get("fallback_triggered"):
        fallback_count += 1

print(f"Routed to cheap: {routed_cheap}")
print(f"Routed to expensive: {routed_expensive}")
print(f"Fallback triggered (cheap failed, escalated): {fallback_count}")