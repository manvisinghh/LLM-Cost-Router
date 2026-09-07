import time
from groq import Groq
from src.config import GROQ_API_KEY, CHEAP_MODEL_NAME, PRICING

client = Groq(api_key=GROQ_API_KEY)


def call_cheap_model(question: str) -> dict:
    start = time.time()

    response = client.chat.completions.create(
        model=CHEAP_MODEL_NAME,
        messages=[{"role": "user", "content": question}],
        temperature=0.3,
    )

    latency = time.time() - start
    answer = response.choices[0].message.content

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    price = PRICING[CHEAP_MODEL_NAME]
    cost = (input_tokens / 1000) * price["input"] + (output_tokens / 1000) * price["output"]

    return {
        "answer": answer,
        "model": CHEAP_MODEL_NAME,
        "latency_sec": round(latency, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
    }