#!/bin/bash
# TRIZ Co-Pilot Service Startup Script
# This script starts all required services for genius-level research

set -e

echo "🚀 Starting TRIZ Co-Pilot Services"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Qdrant is already running
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant is already running${NC}"
else
    echo -e "${YELLOW}📦 Starting Qdrant vector database...${NC}"
    if docker run -d -p 6333:6333 -p 6334:6334 --name triz-qdrant qdrant/qdrant > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Qdrant started successfully${NC}"
        sleep 2
    else
        # Try to start existing container
        if docker start triz-qdrant > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Qdrant container started${NC}"
            sleep 2
        else
            echo -e "${RED}❌ Failed to start Qdrant${NC}"
            echo "   Try: docker rm triz-qdrant && docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant"
        fi
    fi
fi

# Check Qdrant health
echo ""
echo "🔍 Checking Qdrant health..."
if curl -s http://localhost:6333/health | grep -q "ok"; then
    echo -e "${GREEN}✅ Qdrant is healthy${NC}"
else
    echo -e "${RED}❌ Qdrant health check failed${NC}"
fi

# Check if Ollama is running
echo ""
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✅ Ollama is already running${NC}"
else
    echo -e "${YELLOW}🤖 Starting Ollama...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ Ollama started${NC}"
fi

# Check if nomic-embed-text model is available
echo ""
echo "🔍 Checking Ollama model..."
if ollama list | grep -q "nomic-embed-text"; then
    echo -e "${GREEN}✅ nomic-embed-text model is available${NC}"
else
    echo -e "${YELLOW}📥 Pulling nomic-embed-text model (this may take a few minutes)...${NC}"
    ollama pull nomic-embed-text
    echo -e "${GREEN}✅ Model downloaded${NC}"
fi

# Check if books are ingested
echo ""
echo "🔍 Checking knowledge base..."
python3 -c "
from src.triz_tools.services.vector_service import get_vector_service
try:
    vs = get_vector_service()
    info = vs.get_collection_info('triz_documents')
    if info and info['points_count'] > 0:
        print(f'\033[0;32m✅ Knowledge base loaded: {info[\"points_count\"]} document chunks\033[0m')
    else:
        print('\033[1;33m⚠️  No books ingested yet (will use fallback mode)\033[0m')
        print('\033[1;33m   Run: python3 scripts/ingest-books-intelligent.py --test-mode\033[0m')
except Exception as e:
    print(f'\033[1;33m⚠️  Knowledge base not available: {str(e)}\033[0m')
" 2>/dev/null || echo -e "${YELLOW}⚠️  Could not check knowledge base${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}🎉 TRIZ Services Ready!${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Desktop (Cmd+Q, then reopen)"
echo "  2. Look for 🔌 icon in Claude chat"
echo "  3. Ask Claude to solve engineering problems!"
echo ""
echo "Test command:"
echo '  "Check TRIZ system health and then help me with an engineering problem"'
echo ""
