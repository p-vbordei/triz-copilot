#!/usr/bin/env bash
# Setup Claude CLI integration for TRIZ Co-Pilot (TASK-009)
set -e

echo "🚀 Setting up Claude CLI integration for TRIZ Co-Pilot..."
echo ""

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Check if Python 3.11+ is available
echo "✓ Checking Python version..."
if ! python3 -c "import sys; assert sys.version_info >= (3, 11)" 2>/dev/null; then
    echo "❌ Error: Python 3.11 or higher is required"
    exit 1
fi
echo "  Python version OK"

# Install dependencies with uv
echo ""
echo "✓ Installing dependencies..."
if command -v uv &> /dev/null; then
    uv sync
    uv sync --extra claude
    echo "  Dependencies installed with uv"
else
    echo "⚠️  uv not found, using pip..."
    python3 -m pip install -e ".[claude]"
    echo "  Dependencies installed with pip"
fi

# Create Claude configuration directory
echo ""
echo "✓ Creating Claude configuration directory..."
CLAUDE_CONFIG_DIR="$HOME/.config/claude"
mkdir -p "$CLAUDE_CONFIG_DIR/mcp"
echo "  Created: $CLAUDE_CONFIG_DIR/mcp"

# Generate Claude MCP configuration
echo ""
echo "✓ Generating Claude MCP configuration..."
cat > "$CLAUDE_CONFIG_DIR/mcp/triz-copilot.json" << EOF
{
  "name": "triz-copilot",
  "version": "1.0.0",
  "description": "TRIZ Engineering Co-Pilot for Claude",
  "server": {
    "command": "python3",
    "args": [
      "${PROJECT_DIR}/src/claude_mcp_server.py"
    ],
    "env": {
      "PYTHONPATH": "${PROJECT_DIR}",
      "TRIZ_ENV": "production"
    }
  }
}
EOF
echo "  Configuration written to: $CLAUDE_CONFIG_DIR/mcp/triz-copilot.json"

# Create TRIZ sessions directory
echo ""
echo "✓ Creating TRIZ sessions directory..."
TRIZ_DIR="$HOME/.triz"
mkdir -p "$TRIZ_DIR/sessions/active"
mkdir -p "$TRIZ_DIR/sessions/completed"
mkdir -p "$TRIZ_DIR/logs"
echo "  Created: $TRIZ_DIR"

# Check if Qdrant is available (optional)
echo ""
echo "✓ Checking optional dependencies..."
if ! docker ps &> /dev/null; then
    echo "  ⚠️  Docker not running - Qdrant vector search will not be available"
    echo "     The system will fall back to file-based search"
else
    if ! docker ps | grep -q qdrant; then
        echo "  ⚠️  Qdrant not running - starting Qdrant container..."
        docker run -d -p 6333:6333 -p 6334:6334 \
            -v "$TRIZ_DIR/qdrant_data:/qdrant/storage" \
            --name triz-qdrant \
            qdrant/qdrant
        echo "     Qdrant started on port 6333"
    else
        echo "  ✓ Qdrant is running"
    fi
fi

# Check if Ollama is available (optional)
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "  ⚠️  Ollama not running - embeddings will not be generated"
    echo "     Install Ollama from https://ollama.ai"
else
    echo "  ✓ Ollama is running"
    # Check if nomic-embed-text model is available
    if ! ollama list | grep -q nomic-embed-text; then
        echo "     Pulling nomic-embed-text model..."
        ollama pull nomic-embed-text
    fi
    echo "  ✓ nomic-embed-text model available"
fi

# Test the MCP server
echo ""
echo "✓ Testing MCP server..."
if timeout 5 python3 "$PROJECT_DIR/src/claude_mcp_server.py" --version 2>/dev/null; then
    echo "  MCP server test passed"
else
    echo "  Note: MCP server requires stdio input/output (normal behavior)"
fi

# Create a simple test script
echo ""
echo "✓ Creating test script..."
cat > "$PROJECT_DIR/test_claude_integration.sh" << 'EOF'
#!/usr/bin/env bash
# Quick test of Claude integration
echo '{"method": "tools/list", "id": 1}' | python3 src/claude_mcp_server.py
EOF
chmod +x "$PROJECT_DIR/test_claude_integration.sh"
echo "  Created: test_claude_integration.sh"

# Print success message and next steps
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Claude CLI integration setup complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Start Claude CLI:"
echo "   $ claude"
echo ""
echo "2. TRIZ tools will be automatically available:"
echo "   - triz_workflow_start"
echo "   - triz_workflow_continue"
echo "   - triz_solve"
echo "   - triz_get_principle"
echo "   - triz_contradiction_matrix"
echo "   - triz_brainstorm"
echo "   - triz_health_check"
echo ""
echo "3. Test with:"
echo "   $ ./test_claude_integration.sh"
echo ""
echo "4. View logs:"
echo "   $ tail -f ~/.triz/logs/claude_mcp_server.log"
echo ""
echo "📖 Documentation: $PROJECT_DIR/docs/claude-cli-guide.md"
echo ""
