# MCP Server Restart Instructions

## Current Branch: `cli_subprocess`

All changes committed and ready to use.

## For Claude CLI

### Step 1: Stop Current Server
If Claude CLI is currently running with the TRIZ MCP server, close the Claude CLI session.

### Step 2: Restart Claude CLI
```bash
# Claude will automatically reload the MCP server from this directory
claude
```

The server configuration is in your Claude config file (usually `~/.config/claude/config.json` or similar).

## For Gemini CLI

### Step 1: Check Current Process
```bash
# Find any running MCP servers
ps aux | grep mcp_server
```

### Step 2: Kill Existing Process (if any)
```bash
# If you find a process ID from above
kill <PID>
```

### Step 3: Restart Gemini with MCP Server
```bash
# Navigate to project directory
cd /Users/vladbordei/Documents/Development/triz2

# Start Gemini CLI with MCP server
gemini --mcp src/mcp_server.py
```

## Verify Server is Running

### Test CLI Subprocess Availability
```bash
cd /Users/vladbordei/Documents/Development/triz2
python3 scripts/test_cli_subprocess.py
```

Expected output:
```
✅ PASS: CLI Detection
✅ PASS: CLI Executor
✅ PASS: Simple Subprocess
✅ PASS: Research Agent Config
✅ PASS: Materials Analysis

Results: 5/5 tests passed
🎉 ALL TESTS PASSED!
```

### Test Workflow Fix
```bash
python3 test_workflow_fix.py
```

Expected output:
```
✅ WORKFLOW FIX VERIFIED - Solutions are now generated!
```

## What's New After Restart

1. **CLI Subprocess** - 10x research capacity
2. **Research Persistence** - All findings saved to `~/.triz_research/`
3. **Working Workflow** - Actually generates TRIZ solutions

## Quick Test Commands

### Test Workflow
```python
# In Gemini or Claude CLI:
triz_workflow_start()
# Then follow the prompts
```

### Test Research Capacity
```python
# Should show 500 max findings (not 50)
from triz_tools.research_agent import get_research_agent
agent = get_research_agent()
print(f"Max findings: {agent.config['max_findings']}")
# Should print: Max findings: 500
```

### Check Persistence
```bash
# After running any research
ls -la ~/.triz_research/
# Should see session directories
```

## Troubleshooting

### If "CLI not available" warning
```bash
# Install Claude CLI if not present
npm install -g @anthropic-ai/claude-cli

# Or check it's in PATH
which claude
```

### If workflow still not generating solutions
```bash
# Verify you're on correct branch
cd /Users/vladbordei/Documents/Development/triz2
git branch --show-current
# Should show: cli_subprocess

# Check workflow_tools.py has the fix
grep "extract_contradictions" src/triz_tools/workflow_tools.py
# Should return matches
```

### If research not persisting
```bash
# Check directory exists
ls -la ~/.triz_research/
# Should exist and be writable
```

## Ready!

The server should now have:
✅ CLI subprocess integration
✅ Research persistence
✅ Working workflow tools
✅ 10x research capacity

Restart your CLI and test the workflow!
