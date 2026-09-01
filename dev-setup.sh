#!/bin/bash
# Install and run RAG Assistant for development (without Docker)

set -e

echo "=========================================="
echo "🤖 RAG Assistant - Dev Setup"
echo "=========================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

python3 -c 'import sys; print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")' 
echo ""

# Create venv
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create directories
mkdir -p data/sample_docs models

# Generate sample documents
if [ ! -f "data/sample_docs/policy.txt" ]; then
    echo -e "${BLUE}Generating sample documents...${NC}"
    cat > data/sample_docs/policy.txt << 'EOF'
COMPANY POLICIES

Return Policy
The company accepts returns within 30 days of purchase.

Shipping Policy
Free shipping for orders over $50.

Customer Service
Available Monday-Friday, 9AM-6PM EST.
Email: support@company.com

Warranty Information
1-year standard warranty included.

Privacy Policy
Your data is never sold to third parties.
EOF
    echo -e "${GREEN}✓ Sample documents created${NC}"
fi
echo ""

echo -e "${GREEN}=========================================="
echo "✓ Dev Setup Complete!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}To run locally:${NC}"
echo ""
echo "Terminal 1 - Backend:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 - UI:"
echo "  source venv/bin/activate"
echo "  streamlit run ui.py"
echo ""
echo -e "${BLUE}Access:${NC}"
echo "  UI:  http://localhost:8501"
echo "  API: http://localhost:8000"
echo ""
