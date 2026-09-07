import json

with open("evaluation/results/raw_results.json") as f:
    data = json.load(f)

# Simulate an 80/20 easy/hard traffic mix using existing scored data
easy_scored = [e for e in data if e["id"] <= 30 and "quality_score" in e.get("router", {})]
hard_scored = [e for e in data if e["id"] >= 101 and "quality_score" in e.get("router", {})]

# Weight: repeat easy questions to simulate them being 80% of traffic
# (reusing real recorded costs, not re-calling the API)
simulated_mix = easy_scored * 4 + hard_scored  # roughly 80% easy / 20% hard when counts are similar

strategies = ["always_cheap", "always_expensive", "router"]
totals = {s: {"cost": 0.0, "quality": 0.0, "count": 0} for s in strategies}

for entry in simulated_mix:
    for s in strategies:
        data_s = entry[s]
        cost = data_s.get("total_cost_usd", data_s.get("cost_usd", 0))
        totals[s]["cost"] += cost
        totals[s]["quality"] += data_s["quality_score"]
        totals[s]["count"] += 1

print(f"Simulated traffic: {len(easy_scored)*4} easy-weighted + {len(hard_scored)} hard = {len(simulated_mix)} total\n")
print(f"{'Strategy':<20}{'Total Cost':<15}{'Avg Quality':<12}")
print("-" * 47)
for s in strategies:
    n = totals[s]["count"]
    avg_q = totals[s]["quality"] / n
    print(f"{s:<20}${totals[s]['cost']:<14.6f}{avg_q:<12.2f}")

exp_cost = totals["always_expensive"]["cost"]
router_cost = totals["router"]["cost"]
savings = (1 - router_cost / exp_cost) * 100
print(f"\nRouter cost savings vs always-expensive (simulated 80/20 mix): {savings:.1f}%")