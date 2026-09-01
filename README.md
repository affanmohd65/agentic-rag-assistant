# 🤖 Agentic RAG Assistant

An intelligent AI agent that decides whether to answer directly, calculate expressions, or retrieve documents. Built with **Streamlit + FastAPI + Chroma**, fully functional with zero API keys needed (MockLLM included).

## 🚀 Quick Start

### Deploy to Streamlit Cloud (1 Click)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → Select repo → Main file: `streamlit_app.py`
4. Your app is live! ✅

### Run Locally

```bash
# Install
pip install -r requirements.txt

# Run Streamlit UI (all-in-one)
streamlit run streamlit_app.py
# Visit http://localhost:8501
```

## ✨ Features

- **Agent with tool-calling**: Decides to answer directly, calculate, or retrieve documents
- **File upload**: Upload any PDF/TXT file to the knowledge base
- **Chroma vector store**: Local, no external dependencies
- **MockLLM**: Works without API keys (swap in OpenAI/Anthropic via env var)
- **Step-by-step reasoning**: See how the agent makes decisions

## 🎯 Example Queries

```
"Calculate 25 * 4 + 10"              → Uses calculator tool
"What is the return policy?"          → Retrieves from documents
"Tell me about Python"                → Direct answer from LLM
```

## 📦 Project Structure

```
agentic-rag-assistant/
├── streamlit_app.py          # Main entry point (Streamlit Cloud compatible)
├── app/
│   ├── agent.py             # Core agent loop with tool-calling
│   ├── llm_client.py        # LLM abstraction (Mock/OpenAI/Anthropic)
│   ├── retriever.py         # Document ingestion & retrieval (Chroma)
│   ├── tools.py             # Calculator tool
│   ├── main.py              # FastAPI backend (optional)
│   └── __init__.py
├── data/sample_docs/        # Sample documents for testing
├── .streamlit/config.toml   # Streamlit configuration
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── tests/                   # Test suite

Optional (not needed for deployment):
├── .venv/                   # Python virtual environment
├── ui.py                    # Alternative Streamlit UI (use streamlit_app.py instead)
```

## 🔧 How It Works

```
User Query
    ↓
Agent Loop (up to max_steps):
    ├─ Get LLM response
    ├─ LLM decides: direct answer / calculator / retriever
    ├─ Execute tool (if needed)
    ├─ Feed result back to LLM
    └─ Repeat or return answer
    ↓
Display Answer + Reasoning Trace
```

## 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **LLM** | Mock/OpenAI/Anthropic | Zero-cost demo with option for real LLMs |
| **Vector DB** | Chroma (local) | No external service needed |
| **UI** | Streamlit | Simple, interactive, cloud-ready |
| **API** | FastAPI (optional) | Scalable backend if needed |
| **Calculator** | AST-based eval | Safe (no arbitrary code execution) |

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. Create GitHub repo
2. Push code
3. Go to share.streamlit.io → "New app"
4. Select repo, main file: `streamlit_app.py`
5. Done! Get a public URL

### Local Development

```bash
# Install deps
pip install -r requirements.txt

# Run Streamlit
streamlit run streamlit_app.py

# Open browser
http://localhost:8501
```

### FastAPI Backend (Optional)

```bash
# Terminal 1
uvicorn app.main:app --reload
# Endpoint: http://localhost:8000

# Terminal 2
streamlit run ui.py
```

## 📝 Usage

### Upload Documents

1. Open sidebar → "📚 Upload Documents"
2. Select PDF/TXT files
3. Click "Upload & Index"
4. Ask questions about your documents

### Configure Agent

Sidebar → "⚙️ Agent Settings" → Adjust "Reasoning Steps" (1-10)

### Swap LLM Provider

Set environment variable:
```bash
export LLM_PROVIDER=openai  # or anthropic
export OPENAI_API_KEY=sk-...
streamlit run streamlit_app.py
```

Or add secrets in Streamlit Cloud:
```toml
# Streamlit Cloud → App Settings → Secrets
llm_provider = "openai"
openai_api_key = "sk-..."
```

## 🧪 Testing

```bash
pytest tests/
```

## 📊 Interview Points

- ✅ Agent pattern with tool-calling
- ✅ Vector search with Chroma
- ✅ LLM abstraction (Mock/OpenAI/Anthropic)
- ✅ Safe expression evaluation (AST-based)
- ✅ Production-ready Streamlit UI
- ✅ Cloud-deployable on Streamlit Community
- ✅ Works without API keys (MockLLM)

## 🤝 Contributing

Feel free to add more tools or improve the agent loop!

## 📄 License

MIT

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
