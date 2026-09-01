# Quick Start Checklist - Agentic RAG 2.0

## 🚀 Get Started in 5 Minutes

### Option A: Local Python (Recommended for Development)

```bash
# 1. Install dependencies (2 min)
pip install -r requirements.txt

# 2. Initialize database (30 sec)
python -c "from app.database import init_db; init_db()"

# 3. Start API (Terminal 1)
uvicorn app.main:app --reload
# API runs at http://localhost:8000

# 4. Start UI (Terminal 2)
streamlit run streamlit_app.py
# UI runs at http://localhost:8501

# 5. Test API
curl http://localhost:8000/health
# Output: {"status":"ok","version":"2.0.0"}

# 6. Test Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is machine learning?"}'
```

**Total Time:** 5 minutes
**Requirements:** Python 3.11+, pip
**Cost:** Free (uses MockLLM by default)

---

### Option B: Docker (Production-Ready)

```bash
# 1. Start full stack (2 min)
docker-compose up -d

# 2. Wait for services to be healthy
docker-compose ps
# All services should show "healthy" status

# 3. Download model to Ollama (1-5 min, one-time)
docker exec agentic_rag_ollama ollama pull mistral

# 4. Test API
curl http://localhost:8000/health

# 5. Test Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is 5+3?"}'

# 6. View dashboards
# - Jaeger tracing: http://localhost:16686
# - Streamlit UI: http://localhost:8501
# - API Docs: http://localhost:8000/docs
```

**Total Time:** 5-10 minutes (including model download)
**Requirements:** Docker, docker-compose
**Cost:** Free (runs Ollama locally)

---

## ✅ Verification Checklist

### API Endpoints
- [ ] `GET /health` → `{"status":"ok"}`
- [ ] `GET /docs` → Interactive API documentation
- [ ] `POST /query` → Returns answer + reasoning trace
- [ ] `POST /search/hybrid` → Returns ranked results

### Database
- [ ] Tables created in PostgreSQL (or SQLite locally)
- [ ] `python -c "from app.database import SessionLocal; db = SessionLocal()"`
- [ ] No errors = database working

### LLM
- [ ] `ollama pull mistral` (if using Ollama)
- [ ] Test query returns answer (not error)

### Observability (Optional)
- [ ] Jaeger UI at http://localhost:16686 (if running docker-compose)
- [ ] Query appears in trace dashboard

---

## 📊 Common Tasks

### Ingest Documents

```bash
# Upload via API
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@/path/to/document.pdf"

# Or ingest directory
curl -X POST "http://localhost:8000/ingest/directory?directory=/path/to/docs"
```

### Search Documents

```bash
# Hybrid search (recommended)
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","top_k":3}'

# Pure BM25
curl -X POST "http://localhost:8000/search/bm25?query=machine+learning"

# Pure vector search
curl -X POST "http://localhost:8000/search/vector?query=machine+learning"
```

### Get Model Info

```bash
# See available models
curl http://localhost:8000/models/available

# Get routing recommendation
curl -X POST "http://localhost:8000/models/route?task_type=reasoning"
```

### View Performance

```bash
# Get stats
curl http://localhost:8000/stats/performance

# Clear cache
curl -X DELETE http://localhost:8000/cache/clear
```

---

## 🔧 Configuration

### Use Groq (Free, Fastest)

Requires Groq API key (free tier: 40K tokens/min)

```bash
# 1. Get free key at https://console.groq.com
# 2. Set environment
export GROQ_API_KEY=your_api_key
export LLM_PROVIDER=groq

# 3. Restart API
uvicorn app.main:app --reload
```

### Use Claude (Premium)

Requires Anthropic API key (paid)

```bash
export ANTHROPIC_API_KEY=your_api_key
export LLM_PROVIDER=claude

# Restart API
```

### Use Ollama Locally

```bash
# 1. Install Ollama: https://ollama.ai
# 2. Download model
ollama pull mistral

# 3. Set provider
export LLM_PROVIDER=ollama

# 4. API runs against local model
```

### Use PostgreSQL (Production)

```bash
# 1. Install PostgreSQL
# 2. Create database
createdb agentic_rag

# 3. Set connection
export DATABASE_URL=postgresql://user:password@localhost/agentic_rag

# 4. Initialize
python -c "from app.database import init_db; init_db()"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Run from repo root: `cd agentic-rag-assistant` |
| `Port 8000 already in use` | Change port: `uvicorn app.main:app --port 8001` |
| `Database connection error` | Ensure PostgreSQL is running or use SQLite (default) |
| `Ollama connection refused` | Start Ollama: `ollama serve` or `docker-compose up ollama` |
| `No module named 'langgraph'` | Reinstall deps: `pip install -r requirements.txt` |
| `CUDA out of memory` | Use smaller model: `ollama pull orca-mini` |

---

## 📈 Performance Tips

1. **Use Groq for production** (fastest free option)
2. **Enable caching** to avoid redundant queries
3. **Use hybrid search** instead of vector-only
4. **Batch ingest** large document sets
5. **Monitor via Jaeger** to find bottlenecks

---

## 🎓 Learning Resources

| Topic | Resource |
|-------|----------|
| LangGraph | [LangGraph Docs](https://langchain-ai.github.io/langgraph/) |
| LangChain | [LangChain Docs](https://python.langchain.com/) |
| Hybrid Search | [BM25 vs Vector](https://arxiv.org/abs/2304.03679) |
| RAGAS | [RAGAS Metrics](https://github.com/explodinggradients/ragas) |
| Docker | [Docker Compose](https://docs.docker.com/compose/) |
| Langfuse | [Langfuse Docs](https://docs.langfuse.com/) |

---

## 📞 Support

- **Docs:** See UPGRADE_GUIDE.md
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub issues

---

**Last Updated:** 2026
**Version:** 2.0.0
