@echo off
REM Agentic RAG Assistant - Startup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Agentic RAG Assistant
echo ==========================================
echo.

cd /d "%~dp0"

REM Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed
    exit /b 1
)
echo Docker found

REM Check Docker daemon
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker daemon is not running
    exit /b 1
)
echo Docker daemon running
echo.

REM Create directories
if not exist "data\sample_docs" mkdir "data\sample_docs"
if not exist "models" mkdir "models"

REM Generate sample documents
if not exist "data\sample_docs\policy.txt" (
    (
        echo COMPANY POLICIES
        echo.
        echo Return Policy
        echo The company accepts returns within 30 days of purchase for most items in their original condition.
        echo Items must be unused, with all original packaging and tags attached. Refunds are processed within 5-7 business days.
        echo.
        echo Shipping Policy
        echo Free shipping is available for orders over $50. Standard shipping takes 3-5 business days.
        echo Express shipping (1-2 business days is available for $15.
        echo.
        echo Customer Service
        echo Customer service hours are Monday-Friday, 9AM-6PM EST.
        echo You can reach us via email at support@company.com or call 1-800-COMPANY.
        echo.
        echo Warranty Information
        echo All products come with a standard 1-year manufacturer's warranty covering defects.
        echo Extended 3-year warranties are available at time of purchase for an additional fee.
        echo.
        echo Privacy Policy
        echo We collect customer data to improve service and send relevant offers.
        echo Your personal information is never sold to third parties.
    ) > "data\sample_docs\policy.txt"
    echo Sample documents created
)
echo.

echo Starting services...
docker-compose up -d

echo.
timeout /t 5 /nobreak
echo.

echo ==========================================
echo Agentic RAG Assistant Ready!
echo ==========================================
echo.
echo Access:
echo   UI:       http://localhost:8501
echo   API:      http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Commands:
echo   View logs:    docker-compose logs -f
echo   Stop:         docker-compose down
echo   Health check: health-check.bat
echo.

pause
