# 🚀 Step-by-Step GitHub + Streamlit Cloud Deployment

## ✅ Prerequisites Check

You're logged into:
- **Email**: affanmohd65@gmail.com ✅
- **GitHub**: github.com/affanmohd65 ✅
- **Streamlit Cloud**: share.streamlit.io (need to connect)

---

## Step 1️⃣: Create GitHub Repository

### Option A: Using GitHub Website (Easiest)

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name**: `agentic-rag-assistant`
   - **Description**: "Agentic RAG Assistant - AI Agent with tool-calling for interviews"
   - **Visibility**: Public (so Streamlit Cloud can access it)
   - **Initialize repository**: ✅ Add a README
3. Click **"Create repository"**
4. Copy the HTTPS URL: `https://github.com/affanmohd65/agentic-rag-assistant.git`

### Option B: Using GitHub CLI

```powershell
# Install GitHub CLI from https://cli.github.com if you don't have it

gh auth login
# Choose: GitHub.com, HTTPS, Paste authentication token

gh repo create agentic-rag-assistant `
  --public `
  --source=. `
  --description="Agentic RAG Assistant - AI Agent with tool-calling" `
  --remote=origin `
  --push
```

---

## Step 2️⃣: Push Code to GitHub

Run these commands in PowerShell (in your project directory):

```powershell
# Navigate to your project
cd "c:\Users\Mohammad Affan\Desktop\UAE\portfolio-projects\agentic-rag-assistant"

# Initialize git (if not already done)
git init
git branch -M main

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Agentic RAG Assistant

Features:
- AI agent with tool-calling (calculator + retriever)
- Streamlit UI for interactive demos
- Chroma vector database for document search
- PDF and TXT document support
- Mock LLM (works without API keys)
- Ready for cloud deployment"

# Add remote (use your actual repo URL from Step 1)
git remote add origin https://github.com/affanmohd65/agentic-rag-assistant.git

# Push to GitHub
git push -u origin main
```

### If you get authentication error:

```powershell
# Create GitHub Personal Access Token:
# 1. Go to https://github.com/settings/tokens
# 2. Click "Generate new token (classic)"
# 3. Give it: repo (full control), workflow permissions
# 4. Copy the token and use it as password when git prompts

# Or use Git Credentials Manager:
git config --global credential.helper manager

# Then retry:
git push -u origin main
```

---

## Step 3️⃣: Verify on GitHub

1. Go to **https://github.com/affanmohd65/agentic-rag-assistant**
2. Verify you see:
   - ✅ All your files listed
   - ✅ `streamlit_app.py` in root directory
   - ✅ `requirements.txt` with all dependencies
   - ✅ `.streamlit/` folder with config files

If you don't see these, the push failed. Check the error message above.

---

## Step 4️⃣: Connect to Streamlit Cloud

### A. Create Streamlit Account (if needed)

1. Go to **https://share.streamlit.io**
2. Click **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Authorize the app when prompted
5. You'll see "My apps" page

### B. Deploy Your App

1. On Streamlit Cloud dashboard, click **"New app"**
2. In the form, fill:
   - **Repository**: `affanmohd65/agentic-rag-assistant`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
3. Click **"Deploy"**

### C. Wait for Deployment

- You'll see a progress page showing installation
- This takes 5-15 minutes on first deployment
- Watch for the "App is loading" → "App running" transition
- Once complete, you'll get a public URL like:
  ```
  https://affanmohd65-agentic-rag-assistant-xxxxx.streamlit.app
  ```

---

## Step 5️⃣: Test Your Live App

1. Click the URL or open it manually
2. You should see the Agentic RAG Assistant UI
3. Try these test queries:
   - ✅ **"Calculate 100 + 50"** → Should use calculator tool
   - ✅ **"Tell me a fact"** → Should answer directly
   - ✅ **"What is the return policy?"** → Should try to retrieve (if docs loaded)

---

## ⚠️ Troubleshooting

### "App does not exist or you don't have access"

**Cause**: Repository not public or not found

**Fix**:
```powershell
# Make sure remote is set correctly
git remote -v
# Should show: origin https://github.com/affanmohd65/agentic-rag-assistant.git

# Verify on GitHub that repo is PUBLIC
# Go to: Settings → Visibility → Public
```

### "streamlit_app.py not found"

**Cause**: File not pushed to GitHub

**Fix**:
```powershell
# Check if file exists locally
Test-Path streamlit_app.py

# If exists, push again
git add streamlit_app.py
git commit -m "Add streamlit_app.py"
git push origin main

# Redeploy on Streamlit Cloud
```

### App crashes immediately

**Cause**: Missing dependencies

**Fix**:
```powershell
# Make sure all imports are in requirements.txt
pip freeze > requirements.txt

# Add these if missing:
# streamlit>=1.31.0
# chromadb==0.5.5
# PyPDF2>=4.0.0
# fastapi==0.115.0
# uvicorn[standard]==0.30.6

# Commit and push
git add requirements.txt
git commit -m "Update requirements"
git push origin main

# Streamlit will auto-redeploy
```

### Slow performance

**Cause**: First load takes time

**Fix**: This is normal! First load:
- Installs Python & dependencies (~30-60 sec)
- Subsequent loads are much faster

---

## 📊 What Happens After Deployment

Your live app has:

1. **Public URL**: Anyone can access it
   ```
   https://affanmohd65-agentic-rag-assistant-xxxxx.streamlit.app
   ```

2. **Auto-redeploy on git push**:
   ```powershell
   # Make changes locally
   git add .
   git commit -m "Update: ..."
   git push origin main
   
   # App auto-updates within 2 minutes!
   ```

3. **Logs & Settings**:
   - View logs: Click app in Streamlit dashboard → View logs
   - Settings: Click app → Settings → Advanced settings
   - Secrets: Click app → Secrets → Add API keys if needed

---

## 🎯 Next Steps (After Deployment)

### Option 1: Use the Live App
- Share your URL: `https://affanmohd65-agentic-rag-assistant-xxxxx.streamlit.app`
- Anyone can try the agent without setup!

### Option 2: Add Real LLM Keys
```toml
# In Streamlit Cloud dashboard:
# App → Secrets → Add:

llm_provider = "openai"
openai_api_key = "sk-..."
```

### Option 3: Add More Documents
```powershell
# Add documents locally
cd data/sample_docs
# Add .txt and .pdf files

# Commit and push
git add data/
git commit -m "Add documents"
git push origin main

# App auto-redeploys!
```

---

## ✅ Success Checklist

- [ ] Created GitHub repository
- [ ] Pushed code to main branch
- [ ] Connected Streamlit Cloud account
- [ ] Deployed app (selected streamlit_app.py)
- [ ] Received public URL
- [ ] Tested app with sample queries
- [ ] (Optional) Added API keys in secrets
- [ ] (Optional) Added documents

---

## 🎉 You're Live!

Once deployed, your resume point becomes:

> **Deployed an agentic RAG assistant to Streamlit Community Cloud** — a publicly accessible AI agent that demonstrates tool-calling (retrieval + calculator) with step-by-step reasoning traces. Fully functional with zero API keys needed.

**Your URL to share**: [Your public URL will appear here after deployment]

---

**Need help? Check these docs:**
- Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- GitHub help: https://docs.github.com/en/get-started
- Streamlit troubleshooting: https://discuss.streamlit.io
