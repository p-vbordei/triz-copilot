#!/bin/bash
# Restart MCP Server Script

echo "=========================================="
echo "TRIZ MCP Server Restart"
echo "=========================================="
echo ""

# Check current branch
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

if [ "$BRANCH" != "cli_subprocess" ]; then
    echo "⚠️  Warning: Not on cli_subprocess branch"
    echo "   Current: $BRANCH"
    echo "   Expected: cli_subprocess"
    echo ""
    read -p "Switch to cli_subprocess? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout cli_subprocess
        echo "✅ Switched to cli_subprocess"
    fi
fi

echo ""
echo "Checking for running MCP servers..."

# Find MCP server processes
PIDS=$(ps aux | grep -E "(mcp_server|claude_mcp_server)" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ No MCP servers currently running"
else
    echo "Found running MCP server(s):"
    ps aux | grep -E "(mcp_server|claude_mcp_server)" | grep -v grep
    echo ""
    read -p "Kill these processes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$PIDS" | xargs kill
        echo "✅ Killed MCP server processes"
        sleep 1
    fi
fi

echo ""
echo "=========================================="
echo "Server Ready to Restart"
echo "=========================================="
echo ""
echo "Choose your MCP client:"
echo ""
echo "1) Gemini CLI"
echo "2) Claude CLI"
echo "3) Manual restart (I'll do it myself)"
echo ""
read -p "Enter choice (1-3): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo "Starting Gemini CLI with MCP server..."
        echo ""
        echo "Command: gemini --mcp src/mcp_server.py"
        echo ""
        # Note: This will start interactive session
        # User needs to Ctrl+C to exit this script
        gemini --mcp src/mcp_server.py
        ;;
    2)
        echo "Starting Claude CLI..."
        echo ""
        echo "Note: Make sure your Claude config points to this MCP server"
        echo "Config file: ~/.config/claude/config.json"
        echo ""
        echo "Command: claude"
        echo ""
        claude
        ;;
    3)
        echo "Manual restart selected."
        echo ""
        echo "To restart manually:"
        echo ""
        echo "For Gemini:"
        echo "  gemini --mcp src/mcp_server.py"
        echo ""
        echo "For Claude:"
        echo "  claude"
        echo "  (ensure config.json points to this MCP server)"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Testing (Optional)"
echo "=========================================="
echo ""
echo "Run these tests after server starts:"
echo ""
echo "1. Test CLI subprocess:"
echo "   python3 scripts/test_cli_subprocess.py"
echo ""
echo "2. Test workflow fix:"
echo "   python3 test_workflow_fix.py"
echo ""
echo "3. Test in CLI:"
echo "   triz_workflow_start()"
echo ""
