@echo off
REM RAG Assistant - Health Check Script

echo.
echo ==========================================
echo RAG Assistant - Health Check
echo ==========================================
echo.

echo Checking Docker Status...
docker info >nul 2>&1 && echo OK: Docker running || echo FAIL: Docker not running
echo.

echo Checking Containers...
docker ps | find "rag-assistant-backend" >nul && echo OK: Backend running || echo FAIL: Backend not running
docker ps | find "rag-assistant-ui" >nul && echo OK: UI running || echo FAIL: UI not running
echo.

echo Checking API...
curl -s http://localhost:8000/health >nul 2>&1 && echo OK: API responding ^(http://localhost:8000^) || echo FAIL: API not responding
echo.

echo Checking UI...
curl -s http://localhost:8501 >nul 2>&1 && echo OK: UI responding ^(http://localhost:8501^) || echo FAIL: UI not responding
echo.

echo ==========================================
echo URLs:
echo   UI:       http://localhost:8501
echo   API:      http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ==========================================
echo.

pause
