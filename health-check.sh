#!/bin/bash
# RAG Assistant - Health Check Script

echo "=========================================="
echo "🤖 RAG Assistant - Health Check"
echo "=========================================="
echo ""

echo "Checking Docker Status..."
docker info &> /dev/null && echo "✓ Docker running" || echo "✗ Docker not running"
echo ""

echo "Checking Containers..."
docker ps | grep -q "rag-assistant-backend" && echo "✓ Backend running" || echo "✗ Backend not running"
docker ps | grep -q "rag-assistant-ui" && echo "✓ UI running" || echo "✗ UI not running"
echo ""

echo "Checking API..."
curl -s http://localhost:8000/health > /dev/null && echo "✓ API responding (http://localhost:8000)" || echo "✗ API not responding"
echo ""

echo "Checking UI..."
curl -s http://localhost:8501 > /dev/null 2>&1 && echo "✓ UI responding (http://localhost:8501)" || echo "✗ UI not responding"
echo ""

echo "=========================================="
echo "URLs:"
echo "  UI:       http://localhost:8501"
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "=========================================="
