from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import AgenticRAGAssistant
from app.retriever import ingest_directory

app = FastAPI(title="Agentic RAG Assistant")
assistant = AgenticRAGAssistant()


class QueryRequest(BaseModel):
    query: str


class IngestRequest(BaseModel):
    directory: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    n = ingest_directory(req.directory)
    return {"chunks_ingested": n}


@app.post("/query")
def query(req: QueryRequest):
    state = assistant.run(req.query)
    return {"answer": state.final_answer, "trace": state.history}
