# 🚀 Deploy to Streamlit Community Cloud

This guide shows how to deploy the Agentic RAG Assistant to [Streamlit Community Cloud](https://streamlit.io/cloud) so anyone can access it via a public link.

## Prerequisites

- GitHub account ([sign up here](https://github.com/signup))
- Streamlit Community Cloud account ([connect here](https://share.streamlit.io))

## Step-by-Step Deployment

### 1. Push to GitHub

First, initialize a Git repository and push the code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Agentic RAG Assistant"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/agentic-rag-assistant.git
git branch -M main
git push -u origin main
```

### 2. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account if needed
4. Select:
   - **Repository**: `agentic-rag-assistant` (or your repo name)
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **"Deploy"**

### 3. Streamlit Cloud will:

- Install dependencies from `requirements.txt`
- Run `streamlit run streamlit_app.py`
- Generate a public URL: `https://agentic-rag-assistant-{random}.streamlit.app`

### 4. (Optional) Configure Secrets

If you want to use real LLM providers instead of mock:

1. In Streamlit Cloud dashboard, click your app → **Secrets**
2. Add your API keys:

```toml
llm_provider = "openai"
openai_api_key = "sk-..."
```

Or for Anthropic:

```toml
llm_provider = "anthropic"
anthropic_api_key = "sk-ant-..."
```

3. Save and the app will restart automatically

## What's Included

✅ **Fully standalone** - no separate backend needed  
✅ **All dependencies** in `requirements.txt`  
✅ **Document ingestion** for .txt and .pdf files  
✅ **Mock LLM by default** - works without any API keys  
✅ **Calculator tool** - works out of the box  
✅ **Streamlit configuration** - optimized for cloud

## File Structure

```
.streamlit/
├── config.toml          ← UI theme and server settings
└── secrets.toml         ← (local) API keys (don't commit)
streamlit_app.py         ← Main entry point for cloud deployment
requirements.txt         ← All Python dependencies
app/
├── agent.py            ← Core agent loop
├── llm_client.py       ← LLM abstraction (mock/OpenAI/Anthropic)
├── retriever.py        ← Vector search with Chroma
├── tools.py            ← Calculator tool
└── main.py             ← FastAPI backend (for local API mode)
data/
└── sample_docs/        ← Place documents here for ingestion
```

## Testing Locally Before Deploying

Test the standalone app locally first:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then visit `http://localhost:8501`

## Troubleshooting

### App crashes on startup
- Check **View logs** in Streamlit Cloud dashboard
- Look for missing dependencies in `requirements.txt`
- Ensure `streamlit_app.py` is in the root directory

### Document ingestion fails
- Ensure documents are in `data/sample_docs/` in your repo
- Currently supports `.txt` and `.pdf` files
- For PDFs, `PyPDF2` must be installed (it is in requirements.txt)

### Slow performance
- First load may take 30-60s as dependencies install
- Streamlit Cloud is free tier with some resource limits
- Consider upgrading to Streamlit+ for production use

## Sharing Your App

Once deployed, share the public URL:

```
https://agentic-rag-assistant-{random}.streamlit.app
```

Anyone with the link can:
- Ask questions to the agent
- Use the calculator
- Ingest and retrieve documents
- See the reasoning trace

## Next Steps for Production

- Use real LLM provider (OpenAI/Anthropic) via secrets
- Add authentication if needed
- Deploy a separate backend to handle large-scale retrieval
- Use production-grade vector database (Pinecone, Weaviate)
- Add conversation history and persistence
- Monitor usage with Streamlit analytics

---

**Happy deploying!** 🎉

Questions? Check [Streamlit docs](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
