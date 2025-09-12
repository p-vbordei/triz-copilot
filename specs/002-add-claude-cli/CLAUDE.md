# CLAUDE.md - Feature Branch: 002-add-claude-cli

This document provides guidance for implementing Claude CLI integration.

## Current Feature: Claude CLI Integration

**Branch**: `002-add-claude-cli`  
**Status**: Implementation Ready  
**Tasks**: 44 tasks defined in [tasks.md](./tasks.md)

## Quick Start for Implementation

### Starting Point
```bash
# You're on the feature branch
git status  # Should show: On branch 002-add-claude-cli

# Install dependencies (TASK-001)
uv add anthropic-mcp jsonrpc-asyncio aiofiles

# Start with the first task
cat specs/002-add-claude-cli/tasks.md
```

### File Structure to Create

```
src/
├── claude_mcp_server.py         # TASK-002: Main MCP server
├── claude_tools/                 # TASK-005: Tool modules
│   ├── __init__.py
│   ├── parser.py                # TASK-006: Command parsing
│   ├── formatter.py             # TASK-007: Response formatting
│   ├── workflow_handler.py      # TASK-013: Workflow implementation
│   ├── solve_handler.py         # TASK-017: Solve implementation
│   └── direct_handler.py        # TASK-021: Direct tools
└── config/
    └── claude_config.json        # TASK-004: Configuration

tests/
├── unit/
│   ├── test_claude_parser.py    # TASK-029
│   └── test_claude_formatter.py # TASK-030
└── integration/
    └── test_claude_mcp_server.py # TASK-032
```

## Implementation Guidelines

### MCP Server Pattern (TASK-002, TASK-003)
```python
# src/claude_mcp_server.py
import asyncio
import json
import sys
from typing import Dict, Any

class ClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        if method == "tools/list":
            return self._list_tools()
        elif method == "tools/call":
            return await self._call_tool(request.get("params", {}))
        else:
            return {"error": {"code": -32601, "message": "Method not found"}}
```

### Command Parser Pattern (TASK-006)
```python
# src/claude_tools/parser.py
import re
from typing import Dict, Any, Optional

class ClaudeCommandParser:
    PATTERNS = {
        'workflow_start': r'^/triz-workflow$',
        'workflow_continue': r'^/triz-workflow continue (\S+)(?: (.+))?$',
        'solve': r'^/triz-solve (.+)$',
        # Add more patterns
    }
    
    def parse(self, command: str) -> Dict[str, Any]:
        for name, pattern in self.PATTERNS.items():
            match = re.match(pattern, command)
            if match:
                return self._build_result(name, match)
        return {"error": "Unrecognized command"}
```

### Async/Sync Bridge Pattern (TASK-011)
```python
# For CPU-bound TRIZ operations
import asyncio
from triz_tools import workflow_tools

async def handle_workflow_start():
    # Run sync function in thread pool
    result = await asyncio.to_thread(
        workflow_tools.triz_workflow_start
    )
    return result
```

## Testing Approach

### Run Contract Tests First (TASK-035)
```bash
# These will fail initially - that's expected!
pytest specs/002-add-claude-cli/contracts/test_claude_contract.py -v

# Implement until they pass
```

### Test Individual Components
```bash
# Unit tests as you build
pytest tests/unit/test_claude_parser.py -v
pytest tests/unit/test_claude_formatter.py -v

# Integration tests
pytest tests/integration/test_claude_mcp_server.py -v
```

## Common Commands During Development

```bash
# Run specific task tests
pytest -k "test_workflow_start" -v

# Check MCP manifest validity
python -m json.tool < ~/.claude/mcp/triz-copilot.json

# Test MCP server locally
python src/claude_mcp_server.py < test_request.json

# Verify no regression in Gemini
pytest tests/integration/test_gemini_mcp.py -v
```

## Task Tracking

Use this format for commits:
```bash
git add -A
git commit -m "feat(claude): [TASK-001] Install anthropic-mcp dependencies"
git commit -m "feat(claude): [TASK-002] Create basic MCP server structure"
```

## Key Files to Reference

1. **Specification**: `specs/002-add-claude-cli/spec.md` - What to build
2. **Plan**: `specs/002-add-claude-cli/plan.md` - How to build it
3. **Tasks**: `specs/002-add-claude-cli/tasks.md` - Step-by-step tasks
4. **Schema**: `specs/002-add-claude-cli/contracts/claude-mcp-schema.json` - API contract
5. **Contract Tests**: `specs/002-add-claude-cli/contracts/test_claude_contract.py` - Behavior tests

## Current Task Focus

Start with Phase 1, Task 001-012 to establish the foundation:
1. Install dependencies
2. Create MCP server structure
3. Implement protocol handlers
4. Set up tool registration
5. Create parser and formatter
6. Generate manifest and setup script

## Questions to Consider

- How will async handlers interact with sync TRIZ core?
- What's the best way to handle session locking?
- Should we cache vector embeddings for Claude separately?
- How to ensure consistent markdown formatting?

## Next Action

```bash
# Start with TASK-001
uv add anthropic-mcp jsonrpc-asyncio aiofiles

# Then move to TASK-002
touch src/claude_mcp_server.py
# Start implementing based on the plan
```

Remember: Follow TDD - write tests first, make them pass, then refactor!