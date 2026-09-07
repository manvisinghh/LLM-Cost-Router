from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.router.classifier import route_question

app = FastAPI(
    title="LLM Cost Router",
    description="Routes queries between a cheap and expensive LLM based on estimated difficulty.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    routed_to: str
    difficulty_score: int
    fallback_triggered: bool
    total_cost_usd: float
    latency_sec: float


@app.get("/")
def root():
    return {"status": "ok", "service": "LLM Cost Router"}


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = route_question(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")

    return QuestionResponse(
        answer=result["answer"],
        routed_to=result["routed_to"],
        difficulty_score=result["difficulty_score"],
        fallback_triggered=result["fallback_triggered"],
        total_cost_usd=result.get("total_cost_usd", result.get("cost_usd", 0)),
        latency_sec=result["latency_sec"],
    )