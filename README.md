# 🤖 Agentic RAG Assistant

A production-ready agentic RAG system with an intelligent agent that decides whether to:
- **Answer directly** from its knowledge
- **Calculate** mathematical expressions  
- **Retrieve** relevant documents from a knowledge base

Built with FastAPI + Streamlit + Chroma, fully testable with MockLLM (zero API keys needed).
Demonstrates the core LangGraph-style agent pattern in ~150 lines of explainable code.

**🚀 [Deploy to Streamlit Cloud](CLOUD_DEPLOYMENT.md)** - Get a public link in 5 minutes!

## 🚀 Quick Start

### Option A: Deploy to Cloud (Easiest)

Deploy to **Streamlit Community Cloud** with a single click - your app gets a public URL anyone can access:

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → select this repo → `streamlit_app.py`
4. Done! Your app is live.

📖 [**Full cloud deployment guide →**](CLOUD_DEPLOYMENT.md)

### Option B: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit UI (all-in-one)
streamlit run streamlit_app.py
# Visit http://localhost:8501
```

Or use the FastAPI backend + Streamlit UI separately:

```bash
# Terminal 1: Backend API
uvicorn app.main:app --reload

# Terminal 2: Streamlit UI
streamlit run ui.py

# Terminal 3 (optional): Test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 5 + 3?"}'
```

## 🎯 Try It Out

**Examples to test:**
- Math: *"Calculate 25 * 4 + 10"* → Uses calculator tool
- Retrieval: *"What is the return policy?"* → Uses document retrieval (if docs ingested)
- Direct: *"Tell me about Python"* → Answers directly

Watch the **Reasoning Trace** to see how the agent decided which tool to use!

## 🏗️ Architecture

```
User query
   │
   ▼
AgenticRAGAssistant.run()
   │
   ├─► LLM decides: answer directly / call calculator / call retriever
   │
   ├─ calculator(expression) ──► safe AST-based eval (no eval())
   │
   ├─ retriever(query) ──► Chroma vector store (local, sentence-transformers embeddings)
   │        └─ ingest_directory(): chunk → embed → store
   │
   └─► loop feeds tool result back into the prompt, up to max_steps
         │
         ▼
    final_answer + step-by-step trace
```

## Why it's built this way

- **MockLLMClient**: the app and full test suite run with zero API keys
  and zero cost — swap in `OpenAIClient` / `AnthropicClient` (both
  included) via `LLM_PROVIDER` env var for real generation.
- **Chroma + sentence-transformers**: fully local vector search, no paid
  vector DB needed to demo this.
- **Safe calculator**: AST-based evaluation instead of `eval()` —
  a deliberate security choice worth mentioning in interviews.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# in another terminal:
curl -X POST localhost:8000/ingest -H "Content-Type: application/json" -d '{"directory": "data/sample_docs"}'
curl -X POST localhost:8000/query -H "Content-Type: application/json" -d '{"query": "What is the return policy?"}'
```

## Run with Docker

```bash
docker build -t agentic-rag .
docker run -p 8000:8000 agentic-rag
```

## Tests

```bash
pytest -v
```

## What I'd add for a production version

- Real LLM tool-calling APIs (OpenAI/Anthropic function calling) instead
  of the mock rule-based router
- Reranking step after retrieval
- Conversation memory across turns
- An evaluation harness comparing agentic vs. plain-RAG answer quality
  on a fixed query set

## Resume bullet (fill in real numbers once you've run it against real data)

> Built an agentic RAG assistant in Python with tool-calling (retrieval +
> calculator) and a step-by-step reasoning trace, using Chroma for local
> vector search and a swappable LLM client (OpenAI/Anthropic/mock);
> fully tested with CI on every push.
