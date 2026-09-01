@echo off
REM Install and run RAG Assistant for development (without Docker)

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo RAG Assistant - Dev Setup
echo ==========================================
echo.

cd /d "%~dp0"

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    exit /b 1
)
python --version
echo.

REM Create venv
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed
echo.

REM Create directories
if not exist "data\sample_docs" mkdir "data\sample_docs"
if not exist "models" mkdir "models"

REM Generate sample documents
if not exist "data\sample_docs\policy.txt" (
    echo Generating sample documents...
    (
        echo COMPANY POLICIES
        echo.
        echo Return Policy
        echo The company accepts returns within 30 days of purchase.
        echo.
        echo Shipping Policy
        echo Free shipping for orders over $50.
        echo.
        echo Customer Service
        echo Available Monday-Friday, 9AM-6PM EST.
        echo Email: support@company.com
        echo.
        echo Warranty Information
        echo 1-year standard warranty included.
        echo.
        echo Privacy Policy
        echo Your data is never sold to third parties.
    ) > "data\sample_docs\policy.txt"
    echo Sample documents created
)
echo.

echo ==========================================
echo Dev Setup Complete!
echo ==========================================
echo.
echo To run locally:
echo.
echo Terminal 1 - Backend:
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload
echo.
echo Terminal 2 - UI:
echo   venv\Scripts\activate.bat
echo   streamlit run ui.py
echo.
echo Access:
echo   UI:  http://localhost:8501
echo   API: http://localhost:8000
echo.

pause
