import os
from dotenv import load_dotenv

load_dotenv()

# API key — single provider for now (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model names
CHEAP_MODEL_NAME = os.getenv("CHEAP_MODEL_NAME", "openai/gpt-oss-20b")
EXPENSIVE_MODEL_NAME = os.getenv("EXPENSIVE_MODEL_NAME", "openai/gpt-oss-120b")

# Routing thresholds
DIFFICULTY_THRESHOLD = float(os.getenv("DIFFICULTY_THRESHOLD", 3))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.6))

# Per-1K-token pricing (verify at console.groq.com/docs/pricing before final report)
PRICING = {
    CHEAP_MODEL_NAME: {"input": 0.0001, "output": 0.0001},      # gpt-oss-20b
    EXPENSIVE_MODEL_NAME: {"input": 0.00015, "output": 0.0006},  # gpt-oss-120b
}