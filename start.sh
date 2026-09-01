#!/bin/bash
# Agentic RAG Assistant - Startup Script

set -e

echo "=========================================="
echo "🤖 Agentic RAG Assistant"
echo "=========================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📁 Working directory: $PROJECT_ROOT${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon running${NC}"
echo ""

# Create directories
mkdir -p data/sample_docs models

# Generate sample documents
if [ ! -f "data/sample_docs/policy.txt" ]; then
    cat > data/sample_docs/policy.txt << 'EOF'
COMPANY POLICIES

Return Policy
The company accepts returns within 30 days of purchase for most items in their original condition.
Items must be unused, with all original packaging and tags attached. Refunds are processed within 5-7 business days.
Electronics have a separate 15-day return window.

Shipping Policy
Free shipping is available for orders over $50. Standard shipping takes 3-5 business days.
Express shipping (1-2 business days) is available for $15.
International shipping is available to select countries with additional fees.

Customer Service
Customer service hours are Monday-Friday, 9AM-6PM EST.
You can reach us via email at support@company.com or call 1-800-COMPANY.
Average response time for emails is 24 hours.

Warranty Information
All products come with a standard 1-year manufacturer's warranty covering defects.
Extended 3-year warranties are available at time of purchase for an additional fee.
Warranty covers repair or replacement, but not damage from misuse or accidents.

Privacy Policy
We collect customer data to improve service and send relevant offers.
Your personal information is never sold to third parties.
You can opt out of marketing communications at any time by clicking the unsubscribe link.
EOF
    echo -e "${GREEN}✓ Sample documents created${NC}"
fi
echo ""

echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

echo ""
sleep 5

echo -e "${GREEN}=========================================="
echo "✅ Agentic RAG Assistant Ready!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}Access:${NC}"
echo -e "  🎨 UI:        ${BLUE}http://localhost:8501${NC}"
echo -e "  🔧 API:       ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo -e "  View logs:    ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Stop:         ${YELLOW}docker-compose down${NC}"
echo -e "  Health check: ${YELLOW}./health-check.sh${NC}"
echo ""
