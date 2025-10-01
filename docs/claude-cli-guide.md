# Claude CLI Integration Guide

Complete guide for using TRIZ Co-Pilot with Claude CLI.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Claude CLI installed (`claude --version`)
- Docker (optional, for vector search)
- Ollama (optional, for embeddings)

### Installation

1. Clone and navigate to the project:
```bash
git clone https://github.com/yourusername/triz-copilot.git
cd triz-copilot
```

2. Run the Claude setup script:
```bash
./scripts/setup-claude.sh
```

3. Verify installation:
```bash
claude chat
# Tools should be available automatically
```

## Available Tools

### 1. Workflow Mode (Guided Problem-Solving)

**Tool**: `triz_workflow_start`

Start a step-by-step TRIZ workflow session.

```python
# In Claude chat
Use the triz_workflow_start tool
```

**Tool**: `triz_workflow_continue`

Continue an existing workflow session.

```python
# Arguments:
# - session_id: str (from workflow_start)
# - user_input: str (your response)
```

### 2. Autonomous Solve Mode

**Tool**: `triz_solve`

Get a complete TRIZ analysis for your problem.

```python
# Arguments:
# - problem: str (up to 2000 characters)

# Example:
Use triz_solve with problem: "reduce weight while maintaining strength in aircraft wing"
```

### 3. Direct Tool Access

**Tool**: `triz_get_principle`

Get detailed information about a specific TRIZ principle (1-40).

```python
# Arguments:
# - principle_number: int (1-40)

# Example:
Use triz_get_principle with principle_number: 15
```

**Tool**: `triz_contradiction_matrix`

Query the TRIZ contradiction matrix.

```python
# Arguments:
# - improving_parameter: int (1-39)
# - worsening_parameter: int (1-39)

# Example:
Use triz_contradiction_matrix with improving_parameter: 2, worsening_parameter: 14
```

**Tool**: `triz_brainstorm`

Generate contextual ideas using a TRIZ principle.

```python
# Arguments:
# - principle_number: int (1-40)
# - context: str (problem description)

# Example:
Use triz_brainstorm with principle_number: 15, context: "improve flexibility of robotic arm"
```

**Tool**: `triz_health_check`

Check system health and dependencies.

```python
Use triz_health_check
```

## Usage Examples

### Example 1: Complete Workflow Session

```
User: I need help solving an engineering problem systematically.

Claude: I'll help you with that. Let me start a TRIZ workflow.
[Uses triz_workflow_start]

TRIZ Workflow - Problem Definition
Step 1 of 6

Please describe your technical problem or challenge...

User: I need to reduce the weight of a bicycle frame without compromising its strength.

Claude: [Uses triz_workflow_continue with session_id and user input]

TRIZ Workflow - Contradiction Analysis
Step 2 of 6

What is your Ideal Final Result (IFR)?...
```

### Example 2: Quick Problem Analysis

```
User: Analyze this problem: "reduce manufacturing costs while improving product quality"

Claude: I'll perform a TRIZ analysis on your problem.
[Uses triz_solve]

## TRIZ Solution Analysis

### Problem Summary
Cost reduction vs Quality improvement contradiction

### Identified Contradictions
1. Technical Contradiction: Manufacturing expense vs Product quality

### Recommended TRIZ Principles
- #1 - Segmentation: Divide the manufacturing process
- #10 - Preliminary Action: Pre-treat materials
- #35 - Parameter Changes: Alter production parameters

### Solution Concepts
1. **Modular Manufacturing**
   Based on Principle #1
   Divide production into optimized cells...
```

### Example 3: Explore a Specific Principle

```
User: Tell me about TRIZ Principle 15

Claude: [Uses triz_get_principle with principle_number: 15]

## TRIZ Principle 15: Dynamics

### Description
Allow characteristics of an object or system to change to be optimal at each stage...

### Examples
1. Adjustable steering wheel
2. Flexible hose instead of rigid pipe

### Sub-Principles
- **A**: Make it adjustable or adaptive
- **B**: Divide into parts capable of movement
- **C**: If immobile, make it mobile
```

### Example 4: Cross-Platform Session

```
# Start in Claude
User: Start a workflow
Claude: [Uses triz_workflow_start]
Session ID: abc-123-def

# Continue in Gemini (or vice versa)
User: Continue session abc-123-def with input "my problem is..."
# Works seamlessly - sessions are platform-agnostic!
```

## Troubleshooting

### Tools Not Appearing

**Problem**: TRIZ tools don't show up in Claude

**Solutions**:
1. Check MCP configuration:
   ```bash
   cat ~/.config/claude/mcp/triz-copilot.json
   ```

2. Verify Python path:
   ```bash
   which python3
   # Should be Python 3.11+
   ```

3. Test MCP server directly:
   ```bash
   ./test_claude_integration.sh
   ```

4. Check logs:
   ```bash
   tail -f ~/.triz/logs/claude_mcp_server.log
   ```

### Slow Response Times

**Problem**: Tool calls take too long

**Solutions**:
1. Start Qdrant for faster vector search:
   ```bash
   docker run -d -p 6333:6333 qdrant/qdrant
   ```

2. Check Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Review performance benchmarks:
   ```bash
   pytest tests/performance/test_claude_performance.py -v
   ```

### Session Not Found Errors

**Problem**: "Session not found" errors

**Solutions**:
1. Check session directory:
   ```bash
   ls ~/.triz/sessions/active/
   ```

2. Verify session ID is correct (UUID format)

3. Check session hasn't expired (24 hour default):
   ```bash
   # Clean up old sessions
   find ~/.triz/sessions/active/ -mtime +1 -delete
   ```

### Vector Search Failures

**Problem**: Fallback to file-based search

**Solutions**:
1. Ensure Qdrant is running:
   ```bash
   docker ps | grep qdrant
   ```

2. Test Qdrant connection:
   ```bash
   curl http://localhost:6333/collections
   ```

3. Reinitialize knowledge base:
   ```bash
   python src/triz_tools/setup/knowledge_ingestion.py
   ```

## Advanced Configuration

### Custom Configuration

Edit `~/.config/claude/mcp/triz-copilot.json`:

```json
{
  "name": "triz-copilot",
  "server": {
    "command": "python3",
    "args": ["/path/to/src/claude_mcp_server.py"],
    "env": {
      "PYTHONPATH": "/path/to/project",
      "TRIZ_ENV": "production",
      "TRIZ_LOG_LEVEL": "DEBUG"
    }
  }
}
```

### Environment Variables

- `TRIZ_ENV`: `production` or `development`
- `TRIZ_LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `TRIZ_SESSIONS_DIR`: Custom session storage path
- `TRIZ_VECTOR_DB_URL`: Custom Qdrant URL (default: http://localhost:6333)
- `TRIZ_OLLAMA_URL`: Custom Ollama URL (default: http://localhost:11434)

### Session Management

**List active sessions**:
```bash
ls ~/.triz/sessions/active/
```

**View session details**:
```bash
cat ~/.triz/sessions/active/<session-id>.json | jq
```

**Clean up old sessions**:
```bash
find ~/.triz/sessions/active/ -mtime +1 -exec mv {} ~/.triz/sessions/completed/ \;
```

### Performance Tuning

**Increase timeout for complex analyses**:
```json
// In src/config/claude_config.json
{
  "performance": {
    "full_analysis_timeout_ms": 15000
  }
}
```

**Enable caching**:
```json
{
  "features": {
    "enable_caching": true
  }
}
```

## Integration with Other Tools

### Using with Gemini CLI

Sessions are cross-compatible:

```bash
# Start in Claude
claude chat
> Use triz_workflow_start
Session ID: xyz-789

# Continue in Gemini
gemini chat
> /triz-workflow continue xyz-789 "my response"
```

### Standalone Python Usage

```python
from triz_tools import workflow_tools, solve_tools, direct_tools

# Start workflow
response = workflow_tools.triz_workflow_start()
print(response.message)

# Autonomous solve
response = solve_tools.triz_solve_autonomous("reduce weight")
print(response.data)

# Get principle
response = direct_tools.triz_tool_get_principle(15)
print(response.data['principle'])
```

### API Access

```python
import asyncio
from claude_tools.async_utils import run_sync
from claude_tools.workflow_handler import handle_workflow_start

async def main():
    result = await run_sync(handle_workflow_start)
    print(result)

asyncio.run(main())
```

## Best Practices

### 1. Use Descriptive Problem Statements

**Bad**: "make it better"
**Good**: "reduce weight while maintaining strength in aircraft wing structure"

### 2. Follow Workflow Stages

Don't skip ahead - each stage builds on the previous:
1. Problem Definition
2. Contradiction Analysis
3. Principle Selection
4. Solution Generation
5. Evaluation
6. Implementation Planning

### 3. Leverage Session Persistence

Save session IDs for complex problems:
```
Session ID: abc-123-def
# Can return days later and continue
```

### 4. Combine Multiple Principles

Use `triz_brainstorm` with multiple principles for richer solutions.

### 5. Document Your Solutions

Export session data:
```bash
cat ~/.triz/sessions/completed/<session-id>.json | jq '.session_data.solutions'
```

## Additional Resources

- **TRIZ Methodology**: [Official TRIZ Site](https://triz.org)
- **40 Principles**: See `src/data/knowledge_base.json`
- **Contradiction Matrix**: `src/data/contradiction_matrix.csv`
- **API Reference**: `docs/api_reference.md`
- **Issue Tracker**: `https://github.com/yourusername/triz-copilot/issues`

## Support

For help:
- Check logs: `~/.triz/logs/`
- Run health check: Use `triz_health_check` tool
- Report issues: GitHub Issues
- Community: TRIZ forum

## License

MIT License - See LICENSE file for details
