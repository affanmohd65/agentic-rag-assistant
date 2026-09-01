#!/bin/bash
# Quick deployment script for Streamlit Cloud
# Run this to push to GitHub and get deployment instructions

echo "🚀 Agentic RAG Assistant - Cloud Deployment"
echo "==========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📌 Git not initialized. Initializing..."
    git init
    git branch -M main
fi

# Add all changes
echo "📦 Adding files to git..."
git add .

# Commit with deployment message
echo "📝 Creating commit..."
git commit -m "feat: add Streamlit Cloud deployment support

- Added PDF document support (PyPDF2)
- Created standalone streamlit_app.py for cloud deployment
- Added Streamlit configuration (.streamlit/config.toml)
- Updated requirements.txt with all dependencies
- Added comprehensive deployment guides"

echo ""
echo "✅ Changes committed!"
echo ""
echo "📋 Next steps:"
echo "1. Create a GitHub repository at https://github.com/new"
echo "2. Copy the repository URL"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin <YOUR_REPO_URL>"
echo "   git push -u origin main"
echo ""
echo "4. Then go to https://share.streamlit.io"
echo "5. Click 'New app' and select your repository"
echo "6. Select branch: main, file: streamlit_app.py"
echo "7. Click Deploy!"
echo ""
echo "📚 Documentation:"
echo "   - CLOUD_DEPLOYMENT.md   → Step-by-step guide"
echo "   - DEPLOYMENT_SUMMARY.md → Overview & troubleshooting"
echo "   - README.md             → Quick start options"
echo ""
echo "🎉 Your app will be live at:"
echo "   https://your-username-agentic-rag-assistant-xxxxx.streamlit.app"
