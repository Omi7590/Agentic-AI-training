# RTI Mitra - main.py
# FastAPI service exposing RTI rule records.
#
# Routes:
#   GET  /health
#   GET  /records?limit=
#   GET  /records/{id}
#   GET  /search?q=
#   POST /questions

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from app.records import load_records, get_by_id
from app.smart_search import smart_search

from app.llm import chat as llm_chat
from app.vectorstore import semantic_search as vector_search
from app.rag import ask as rag_ask
from app.agent_loop import run_agent
from app.graph import run_graph


app = FastAPI(
    title="RTI Mitra API",
    description="Explains the RTI Act and helps draft RTI applications.",
    version="0.1.0",
)

# ── request / response models ──────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    answer: str

# ── routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Check that the service is running."""
    return {"status": "ok", "service": "RTI Mitra"}

@app.get("/records")
def get_records(limit: int = Query(default=10, ge=1, le=100)):
    """Return up to `limit` RTI rule records."""
    records = load_records()
    return {"total": len(records), "limit": limit, "records": records[:limit]}

@app.get("/records/{record_id}")
def get_record(record_id: int):
    """Return a single record by its 1-based ID. Returns 404 if not found."""
    record = get_by_id(record_id - 1)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found.")
    return record

@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
    """Search records using TF-IDF cosine similarity."""
    results = smart_search(q)
    return {"query": q, "total": len(results), "results": results}

@app.post("/questions", response_model=QuestionResponse)
def ask_question(body: QuestionRequest):
    """
    Accept a plain-language RTI question and return the best-matching rule.
    (Day 4: keyword match; will be replaced with RAG on Day 8.)
    """
    results = smart_search(body.question, top_k=1)
    if results:
        answer = f"{results[0]['rule']} (Ref: {results[0]['section_or_rule_ref']})"
    else:
        answer = "No matching rule found. Please try a different question."
    return QuestionResponse(question=body.question, answer=answer)


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest):
    """Send a message to RTI Mitra and get a grounded answer."""
    try:
        result = llm_chat(body.message)
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/semantic")
def semantic_search_endpoint(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
):
    """Semantic search using sentence-transformer embeddings and Chroma."""
    results = vector_search(q, top_k=top_k)
    return {"query": q, "total": len(results), "results": results}


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list
    chunks_used: int


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(body: AskRequest):
    """RAG endpoint: retrieves RTI rules from Chroma and answers with citations."""
    try:
        result = rag_ask(body.question, top_k=body.top_k)
        return AskResponse(question=body.question, **result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentRequest(BaseModel):
    question: str
    thread_id: str = "default"
    use_langgraph: bool = True
    approval: str = None


class AgentResponse(BaseModel):
    question: str
    answer: str
    thread_id: str
    pending_approval: bool = False


@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(body: AgentRequest):
    """
    Agent endpoint with LangGraph memory + interrupt approval step.
    - First call: send question. If draft_rti is triggered, returns pending_approval=True.
    - Second call: send same thread_id with approval='yes' to resume.
    - Set use_langgraph=false to use the hand-written agent loop instead.
    """
    try:
        if body.use_langgraph:
            result = run_graph(
                body.question,
                thread_id=body.thread_id,
                approval=body.approval,
            )
        else:
            result = run_agent(body.question)
            result["thread_id"] = body.thread_id
            result["pending_approval"] = False
        return AgentResponse(**{k: v for k, v in result.items()
                                if k in AgentResponse.model_fields})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
