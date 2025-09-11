# TRIZ Co-Pilot Integration Guide

## Overview

TRIZ Co-Pilot extends Google Gemini CLI with systematic innovation capabilities using the Theory of Inventive Problem Solving (TRIZ) methodology.

## Installation

### Prerequisites
- Python 3.11+
- Google Gemini CLI installed
- uv package manager (optional but recommended)

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd triz2
```

2. **Install dependencies:**
```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

3. **Verify installation:**
```bash
python3 src/cli.py --version
```

## Integration Methods

### Method 1: Standalone CLI

Use TRIZ Co-Pilot directly from the command line:

```bash
# Get principle details
python3 src/cli.py tool principle 1

# Query contradiction matrix
python3 src/cli.py tool matrix 1 14

# Solve a problem
python3 src/cli.py solve "Reduce weight while maintaining strength"

# Start interactive mode
python3 src/cli.py interactive
```

### Method 2: Gemini CLI Integration (MCP)

1. **Copy configuration to Gemini config directory:**
```bash
cp gemini-cli-config.toml ~/.gemini/tools/triz-copilot.toml
```

2. **Use in Gemini:**
```
/triz-workflow start
/triz-tool get-principle 1
/triz-solve "Your problem description"
```

### Method 3: Python API

```python
from src.triz_tools.solve_tools import triz_solve_autonomous
from src.triz_tools.direct_tools import triz_tool_get_principle

# Autonomous solve
response = triz_solve_autonomous("Reduce vibration in machinery")
if response.success:
    print(response.data['solution_concepts'])

# Get principle
principle = triz_tool_get_principle(15)
print(principle.data['description'])
```

## Available Commands

### Workflow Commands
- `/triz-workflow start` - Begin guided TRIZ session
- `/triz-workflow continue [session_id] [input]` - Continue session
- `/triz-workflow reset [session_id]` - Reset session

### Direct Tools
- `/triz-tool get-principle [1-40]` - Get principle details
- `/triz-tool contradiction-matrix [improving] [worsening]` - Query matrix
- `/triz-tool brainstorm [principle] [context]` - Generate ideas

### Autonomous Solve
- `/triz-solve [problem description]` - Full TRIZ analysis

## Examples

### Example 1: Weight Reduction Problem
```bash
python3 src/cli.py solve "Reduce weight of aircraft wing while maintaining structural integrity"
```

### Example 2: Manufacturing Optimization
```bash
python3 src/cli.py solve "Increase production speed by 50% while reducing defects"
```

### Example 3: Guided Workflow
```bash
# Start session
python3 src/cli.py workflow start
# Note the session ID

# Continue with problem description
python3 src/cli.py workflow continue [session_id] "Reduce noise from motor"

# Follow prompts to complete analysis
```

## Architecture

```
triz2/
├── src/
│   ├── triz_tools/
│   │   ├── models/          # Data models
│   │   ├── workflow_tools.py # Guided workflow
│   │   ├── direct_tools.py   # Direct tool access
│   │   └── solve_tools.py    # Autonomous solver
│   ├── mcp_server.py         # Gemini MCP server
│   └── cli.py                # CLI interface
├── data/
│   ├── triz_principles.txt   # 40 principles
│   └── contradiction_matrix.json # 39x39 matrix
└── tests/
    └── contract/              # TDD contract tests
```

## Performance

- Tool queries: < 2 seconds
- Autonomous solve: < 10 seconds
- Memory usage: < 1GB

## Testing

Run all tests:
```bash
PYTHONPATH=. python3 -m pytest tests/contract/*_green.py -v
```

## Troubleshooting

### Issue: Command not found
**Solution:** Ensure PYTHONPATH is set:
```bash
export PYTHONPATH=/path/to/triz2
```

### Issue: Session not found
**Solution:** Sessions are stored in `./sessions/`. Check if directory exists and has write permissions.

### Issue: Slow performance
**Solution:** The first run may be slower as it loads knowledge bases. Subsequent runs use cached data.

## Future Enhancements

- [ ] Qdrant vector database for semantic search
- [ ] Ollama embeddings for similarity matching
- [ ] Web UI interface
- [ ] Extended knowledge base with patents
- [ ] Multi-language support

## Contributing

See CONTRIBUTING.md for development guidelines.

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions:
- GitHub Issues: [repository-issues-url]
- Documentation: See /docs directory
- Examples: See /examples directory