@echo off
REM Quick deployment script for Streamlit Cloud (Windows)

echo.
echo ========================================
echo Agentic RAG Assistant - Cloud Deployment
echo ========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    git branch -M main
)

REM Add all changes
echo Adding files to git...
git add .

REM Commit with deployment message
echo Creating commit...
git commit -m "feat: add Streamlit Cloud deployment support"

echo.
echo ===== SUCCESS! =====
echo.
echo Next steps:
echo.
echo 1. Create a GitHub repository: https://github.com/new
echo 2. Copy the repository URL
echo 3. Run these commands in PowerShell:
echo.
echo    git remote add origin [YOUR_REPO_URL]
echo    git push -u origin main
echo.
echo 4. Go to https://share.streamlit.io
echo 5. Click 'New app' and connect your GitHub account
echo 6. Select:
echo    - Repository: your repo name
echo    - Branch: main
echo    - File: streamlit_app.py
echo 7. Click Deploy!
echo.
echo After ~5-10 minutes, your app will be live at:
echo https://your-username-agentic-rag-assistant-xxxxx.streamlit.app
echo.
echo Documentation:
echo   - CLOUD_DEPLOYMENT.md   - Detailed step-by-step guide
echo   - DEPLOYMENT_SUMMARY.md - Overview and troubleshooting
echo   - README.md             - Quick start options
echo.
pause
