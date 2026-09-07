import json
import csv
import os

RESULTS_PATH = "evaluation/results/raw_results.json"
SUMMARY_CSV_PATH = "evaluation/results/summary.csv"


def build_report():
    with open(RESULTS_PATH, "r") as f:
        results = json.load(f)

    strategies = ["always_cheap", "always_expensive", "router"]
    totals = {s: {"cost": 0.0, "latency": 0.0, "quality": 0.0, "count": 0} for s in strategies}

    for entry in results:
        if "error" in entry:
            continue
        for s in strategies:
            if s not in entry or "quality_score" not in entry[s]:
                continue
            data = entry[s]
            cost = data.get("total_cost_usd", data.get("cost_usd", 0))
            totals[s]["cost"] += cost
            totals[s]["latency"] += data.get("latency_sec", 0)
            totals[s]["quality"] += data["quality_score"]
            totals[s]["count"] += 1

    print(f"{'Strategy':<20}{'Total Cost':<15}{'Avg Latency':<15}{'Avg Quality':<12}{'N':<5}")
    print("-" * 67)

    rows = []
    for s in strategies:
        n = totals[s]["count"]
        if n == 0:
            continue
        avg_latency = totals[s]["latency"] / n
        avg_quality = totals[s]["quality"] / n
        total_cost = totals[s]["cost"]
        print(f"{s:<20}${total_cost:<14.6f}{avg_latency:<15.3f}{avg_quality:<12.2f}{n:<5}")
        rows.append({
            "strategy": s,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_sec": round(avg_latency, 3),
            "avg_quality_score": round(avg_quality, 2),
            "n": n,
        })

    os.makedirs(os.path.dirname(SUMMARY_CSV_PATH), exist_ok=True)
    with open(SUMMARY_CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSummary saved to {SUMMARY_CSV_PATH}")

    # Cost savings vs always-expensive
    if totals["always_expensive"]["count"] and totals["router"]["count"]:
        exp_cost = totals["always_expensive"]["cost"]
        router_cost = totals["router"]["cost"]
        savings_pct = (1 - router_cost / exp_cost) * 100 if exp_cost > 0 else 0
        print(f"\nRouter cost savings vs always-expensive: {savings_pct:.1f}%")


if __name__ == "__main__":
    build_report()