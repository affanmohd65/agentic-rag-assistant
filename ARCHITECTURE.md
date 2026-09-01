# 🏗️ Architecture & Deployment Options

## Local Development (API Mode)

```
┌──────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                            │
│                                                                  │
│  ┌─────────────────────┐         ┌──────────────────────────┐   │
│  │  Terminal 1         │         │  Terminal 2              │   │
│  │  Backend API        │         │  Streamlit UI            │   │
│  │                     │         │                          │   │
│  │  uvicorn app...     │◄────────┤  streamlit run ui.py     │   │
│  │  http://localhost   │         │  http://localhost:8501   │   │
│  │  :8000              │         │                          │   │
│  │                     │         │  User Interface          │   │
│  │  • /health          │         │  • Text input            │   │
│  │  • /query           │         │  • Submit button         │   │
│  │  • /ingest          │         │  • Results display       │   │
│  │  • /docs (Swagger)  │         │  • Reasoning trace       │   │
│  └─────────────────────┘         └──────────────────────────┘   │
│           ▲                                                      │
│           │                                                      │
│           └──── App Logic ─────┬─────────────────────────────┐  │
│                                │                             │   │
│  ┌─────────────────────────────┴─────────────────────────┐   │   │
│  │ app/                                                   │   │   │
│  │ ├── agent.py       (Core agent loop)                  │   │   │
│  │ ├── llm_client.py  (LLM abstraction)                  │   │   │
│  │ ├── retriever.py   (Vector search + Chroma)           │   │   │
│  │ ├── tools.py       (Calculator)                       │   │   │
│  │ └── main.py        (FastAPI server)                   │   │   │
│  │                                                       │   │   │
│  │ data/                                                 │   │   │
│  │ └── sample_docs/   (Documents to ingest)             │   │   │
│  │                                                       │   │   │
│  │ .chroma/           (Vector DB - Chroma)              │   │   │
│  └───────────────────────────────────────────────────────┘   │   │
└──────────────────────────────────────────────────────────────────┘
         Only accessible at http://localhost:8501
```

## Cloud Deployment (Streamlit Cloud)

```
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT COMMUNITY CLOUD                  │
│                                                         │
│  YOUR-APP.streamlit.app (Public URL)                   │
│  Accessible from: Anywhere! Just share the link        │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │  Streamlit App Container                       │   │
│  │                                                │   │
│  │  streamlit run streamlit_app.py                │   │
│  │                                                │   │
│  │  ┌──────────────────────────────────────────┐ │   │
│  │  │  Web Interface (built into streamlit)   │ │   │
│  │  │  • Text input & buttons                 │ │   │
│  │  │  • Results display                      │ │   │
│  │  │  • Reasoning trace                      │ │   │
│  │  └──────────────────────────────────────────┘ │   │
│  │                ▲                              │   │
│  │                │                              │   │
│  │  ┌────────────┴───────────────────────────┐   │   │
│  │  │  Agent Logic (Direct - No API Call)   │   │   │
│  │  │                                        │   │   │
│  │  │  from app.agent import ...             │   │   │
│  │  │  assistant = AgenticRAGAssistant()     │   │   │
│  │  │                                        │   │   │
│  │  │  ├─ agent.py   (Core loop)             │   │   │
│  │  │  ├─ llm_client.py (MockLLM default)   │   │   │
│  │  │  ├─ retriever.py (Chroma search)      │   │   │
│  │  │  ├─ tools.py (Calculator)             │   │   │
│  │  │  └─ .chroma/ (In-memory vector DB)    │   │   │
│  │  │                                        │   │   │
│  │  └────────────────────────────────────────┘   │   │
│  │                                                │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  Deployed from: GitHub (auto-redeploys on git push)   │
│  Dependencies: requirements.txt installed automatically│
│  Accessible: https://your-username-app.streamlit.app  │
└─────────────────────────────────────────────────────────┘
              Public internet access for anyone!
```

## Data Flow in Agent

```
User Input
    │
    ▼
┌─────────────────────────┐
│  Streamlit Text Area    │
└────────────┬────────────┘
             │
             ▼
    ┌────────────────┐
    │  streamlit_app │
    │  (or ui.py)    │
    └────────┬───────┘
             │
             ▼
┌────────────────────────────────┐
│  AgenticRAGAssistant.run()     │
│                                │
│  For each step (max_steps=3):  │
│  1. Call LLM with prompt       │
│  ├─ LLM returns: answer OR     │
│  │  tool_call (calculator/     │
│  │  retriever)                 │
│  │                             │
│  2. If tool_call:              │
│  │  ├─ calculator(expr)        │
│  │  └─ retriever(query)        │
│  │                             │
│  3. Feed result back to LLM    │
│  4. Loop until answer found    │
└────────────┬───────────────────┘
             │
             ▼
    ┌─────────────────┐
    │  Final Answer   │
    │  + History      │
    │  (Reasoning)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │  Display in Streamlit UI    │
    │  • Answer in green box      │
    │  • Trace with steps         │
    │  • Tool calls shown         │
    └─────────────────────────────┘
```

## LLM Client Hierarchy

```
                    BaseLLMClient (Abstract)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   MockLLMClient      OpenAIClient       AnthropicClient
   (Default)          (Real)              (Real)
   
┌─ MockLLMClient ─┐
│ Deterministic   │
│ Rule-based      │
│ No API key      │
│ For demos/tests │
└─────────────────┘

Activated via:
  - LLM_PROVIDER env var
  - llm_provider in secrets.toml
  - get_llm_client() function
```

## File Deployment Structure

```
GitHub Repository
│
├── .github/              (Optional: CI/CD workflows)
├── .streamlit/
│   ├── config.toml      ← Cloud UI settings
│   └── secrets.toml     ← API keys (gitignored)
├── app/
│   ├── __init__.py
│   ├── agent.py         ← Core agent (150 lines)
│   ├── llm_client.py    ← LLM abstraction
│   ├── retriever.py     ← Vector search (FIXED: PDF support)
│   ├── tools.py         ← Calculator
│   └── main.py          ← FastAPI (optional)
├── data/
│   └── sample_docs/     ← Place your documents here
│       ├── policy.txt
│       └── *.pdf        ← NEW: PDF support
├── tests/
│   ├── test_agent.py
│   └── test_tools.py
├── streamlit_app.py     ← ⭐ MAIN: Cloud entry point
├── ui.py                ← Alternative: API mode entry
├── requirements.txt     ← Dependencies (includes PyPDF2)
├── .gitignore           ← Updated for cloud
├── README.md            ← Updated with cloud quickstart
├── CLOUD_DEPLOYMENT.md  ← Step-by-step guide
├── DEPLOYMENT_SUMMARY.md ← Overview
├── QUICK_DEPLOY_GUIDE.md ← This guide
└── docker-compose.yml   ← Optional: local Docker

⭐ = Most important for Streamlit Cloud
```

---

## Key Differences: Local vs Cloud

| Aspect | Local API | Local Standalone | Cloud |
|--------|-----------|------------------|-------|
| **Entry Point** | `ui.py` | `streamlit_app.py` | `streamlit_app.py` |
| **Backend** | Separate uvicorn | Embedded | Embedded in Streamlit |
| **Accessibility** | localhost only | localhost only | Public internet |
| **Configuration** | API URL config | N/A | Streamlit Cloud secrets |
| **Startup** | Manual (2 terminals) | `streamlit run` | Auto on git push |
| **Scalability** | Limited | Limited | Cloud managed |
| **Cost** | Free (local) | Free (local) | **Free!** (community tier) |

---

## Deployment Decision Tree

```
Are you developing?
│
├─ YES → Use LOCAL API MODE
│        - Terminal 1: uvicorn app.main:app --reload
│        - Terminal 2: streamlit run ui.py
│        - Test at http://localhost:8501
│        - Good for debugging backend & UI separately
│
└─ NO, ready to deploy?
   │
   ├─ Want it on your computer only?
   │  └─ Use STANDALONE MODE
   │     - streamlit run streamlit_app.py
   │     - Works offline
   │     - No internet needed
   │
   └─ Want it on the internet?
      └─ Use STREAMLIT CLOUD
         - Push to GitHub
         - Deploy at share.streamlit.io
         - Public URL anyone can access
         - ✅ THIS IS WHAT YOU WANT! ✅
```

---

**Ready to deploy? See QUICK_DEPLOY_GUIDE.md for 3-step instructions!**
