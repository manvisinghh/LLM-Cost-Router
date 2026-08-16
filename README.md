# LLM Cost Router

An intelligent router designed to optimize API costs and latency by dynamic prompt classification and fallback escalation.

## Project Structure

```text
LLM-Cost-Router/
├── src/
│   ├── __init__.py
│   ├── router/
│   │   ├── __init__.py
│   │   ├── classifier.py      # Difficulty scoring / routing logic
│   │   └── fallback.py        # Confidence check + escalation logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cheap_model.py     # Wrapper for small/fast model API
│   │   └── expensive_model.py # Wrapper for large model API
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI app, /ask endpoint
│   └── config.py              # Model names, API keys loading, thresholds
├── evaluation/
│   ├── dataset.py             # Builds/loads test question set
│   ├── run_eval.py            # Runs always-cheap / always-expensive / router
│   └── results/               # CSVs, charts get saved here
├── data/
│   └── test_questions.json    # ~100-200 labeled/unlabeled questions
├── tests/
│   ├── test_router.py
│   └── test_models.py
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── .env.example               # Template for API keys
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml
