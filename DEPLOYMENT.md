# 🤖 Agentic RAG Assistant - Deployment Guide

A production-ready agentic RAG system with interactive Streamlit UI and FastAPI backend.

## 🚀 Quick Start (30 seconds)

### Windows
```batch
start.bat
```

### macOS / Linux
```bash
chmod +x start.sh
./start.sh
```

## 🌐 Access

| URL | Purpose |
|-----|---------|
| http://localhost:8501 | **Streamlit UI** - Interactive Q&A interface |
| http://localhost:8000 | **FastAPI Backend** |
| http://localhost:8000/docs | **API Documentation** (Swagger UI) |

## ✨ Features

- **Agent Loop**: LLM decides between tools (answer directly, retrieve docs, calculate)
- **Vector Search**: Chroma + sentence-transformers (local, no API keys)
- **Safe Calculator**: AST-based evaluation (not `eval()`)
- **Document Ingestion**: Upload and query custom documents
- **Reasoning Trace**: See exactly how the agent decided

## 🔧 How to Use

### Start Services
```bash
./start.sh          # macOS/Linux
start.bat           # Windows
```

### Run Health Check
```bash
./health-check.sh   # macOS/Linux
health-check.bat    # Windows
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f backend  # Specific service
```

### Stop Services
```bash
docker-compose down
```

### Reset Everything
```bash
docker-compose down -v
rm -rf data/sample_docs/* models/*
./start.sh
```

## 📚 API Endpoints

### Ingest Documents
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "data/sample_docs"}'
```

### Query the Agent
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the return policy?"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🎬 Interview Demo Flow

1. **Show the UI** (http://localhost:8501)
2. **Ask factual question**: "What is the return policy?"
   - Shows retrieval from documents
3. **Ask math question**: "Calculate 100 * 2 + 50"
   - Shows calculator tool use
4. **Ask opinion**: "Who is the best CEO?"
   - Shows direct answer (no tools needed)
5. **Click trace expanders** to show reasoning
6. **Ingest new documents** live via the UI
7. **Discuss architecture** (show code)

## 🏗️ Architecture

```
┌─ UI (Streamlit, 8501) ─────┐
│                             │
│  Query Interface            │
│  Document Ingestion         │
│  Reasoning Trace Display    │
│                             │
└──────────────┬──────────────┘
               │
         HTTP  │
               ▼
┌─ Backend (FastAPI, 8000) ──┐
│                             │
│  Agent Loop                 │
│  ├─ Tool: Retriever         │
│  ├─ Tool: Calculator        │
│  └─ Tool: Direct Answer     │
│                             │
│  Chroma Vector Store        │
│                             │
└─────────────────────────────┘
```

## 📋 Project Structure

```
agentic-rag-assistant/
├── ui.py                    # Streamlit interface
├── docker-compose.yml       # Service orchestration
├── start.sh / start.bat     # Startup scripts
├── health-check.*           # Health verification
├── requirements.txt         # Dependencies
├── Dockerfile              # Container image
├── README.md               # Project overview
├── DEPLOYMENT.md           # This file
├── app/
│   ├── main.py            # FastAPI app
│   ├── agent.py           # Agent loop
│   ├── retriever.py       # Vector search
│   ├── tools.py           # Calculator & helpers
│   ├── llm_client.py      # LLM interface
│   └── __init__.py
├── data/
│   └── sample_docs/       # Knowledge base
└── models/                # Embeddings/vectors
```

## 🔧 Configuration

### Environment Variables

Create `.env` file or edit in `docker-compose.yml`:

```bash
# LLM Provider
LLM_PROVIDER=mock           # Use 'openai' for production

# API Keys (if using real LLM)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Ports
RAG_BACKEND_PORT=8000
RAG_UI_PORT=8501
```

### Document Path

Change document ingestion path in UI or via API:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "data/custom_docs"}'
```

## 🐛 Troubleshooting

### "Services won't start"
```bash
# Check Docker is running
docker ps

# View detailed logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
```

### "UI not loading"
- Wait 10-15 seconds for Streamlit to start
- Refresh browser (Ctrl+R)
- Check logs: `docker-compose logs ui`

### "API returns 503 - Model not loaded"
- Ingest documents first: Use UI or call /ingest endpoint
- Check backend logs: `docker-compose logs backend`

### "Port already in use"
```bash
# Find what's using the port
lsof -i :8000      # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Change ports in docker-compose.yml and restart
```

### "Cannot write to /data directory"
```bash
# Reset permissions
docker-compose down -v
rm -rf data/* models/*
chmod 777 data models
./start.sh
```

## 🎯 Common Use Cases

### Demo with Your Own Documents

1. Place documents in `data/custom_docs/`
2. In UI, change directory path to `data/custom_docs`
3. Click "Ingest Documents"
4. Start querying

### Switch to Real LLM

```bash
# Set environment variable
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-key

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Increase Model Context

Edit `app/agent.py`:
```python
max_steps=10  # Increase from default
```

### Add More Tools

Edit `app/tools.py` and `app/agent.py` to add new tools (web search, database query, etc.)

## 📊 Performance Tips

1. **Faster Inference**: Use smaller embedding model
   - Edit `app/retriever.py`: `model_name="all-MiniLM-L6-v2"`

2. **Better Accuracy**: Use larger LLM
   - Swap mock → OpenAI GPT-4

3. **Larger Knowledge Base**: Use cloud vector DB
   - Replace Chroma with Pinecone/Weaviate

## 🔐 Security Notes

- ✅ **Safe Evaluation**: AST-based calc (not `eval()`)
- ✅ **Local-First**: All data stays local (Chroma)
- ⚠️ **Production**: Add authentication, rate limiting, input validation

## 📈 Scaling Considerations

| Aspect | Current | Production |
|--------|---------|------------|
| **Users** | 1 (demo) | Add load balancer |
| **Documents** | ~100 | Add document management system |
| **Latency** | ~2s | Cache responses, optimize embeddings |
| **Cost** | Free | Use cheap embedding API |
| **Availability** | Local only | Deploy to cloud (AWS/GCP/Azure) |

## 🆘 Support

1. Check [Troubleshooting](#-troubleshooting) above
2. Run health check: `./health-check.sh`
3. Review logs: `docker-compose logs -f`
4. See main README.md for architecture details

## 📄 Next Steps

- [ ] Ingest custom documents
- [ ] Test with different queries
- [ ] Add more tools
- [ ] Integrate real LLM
- [ ] Deploy to cloud
- [ ] Add monitoring/logging

---

**Ready to demo? Run `start.sh` or `start.bat`! 🚀**
