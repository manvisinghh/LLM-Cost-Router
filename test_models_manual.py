from src.router.classifier import route_question

print("=== Router test: easy question ===")
result = route_question("What is the capital of France?")
print(f"Routed to: {result['routed_to']}")
print(f"Difficulty score: {result['difficulty_score']}")
print(f"Fallback triggered: {result['fallback_triggered']}")
print(f"Total cost: ${result['total_cost_usd']}")
print(f"Answer: {result['answer'][:200]}")

print("\n=== Router test: hard/obscure question ===")
result = route_question(
    "Explain the Byzantine Generals Problem in distributed systems, "
    "with a concrete failure scenario."
)
print(f"Routed to: {result['routed_to']}")
print(f"Difficulty score: {result['difficulty_score']}")
print(f"Fallback triggered: {result['fallback_triggered']}")
print(f"Total cost: ${result['total_cost_usd']}")
print(f"Answer: {result['answer'][:200]}")