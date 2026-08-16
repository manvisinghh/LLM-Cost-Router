import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model names
CHEAP_MODEL_NAME = os.getenv("CHEAP_MODEL_NAME", "llama-3.2-3b-preview")
EXPENSIVE_MODEL_NAME = os.getenv("EXPENSIVE_MODEL_NAME", "gpt-4o")

# Routing thresholds
DIFFICULTY_THRESHOLD = float(os.getenv("DIFFICULTY_THRESHOLD", 3))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.6))

# Rough per-1K-token pricing for cost tracking (update with real numbers later)
PRICING = {
    CHEAP_MODEL_NAME: {"input": 0.00005, "output": 0.00008},
    EXPENSIVE_MODEL_NAME: {"input": 0.0025, "output": 0.01},
}