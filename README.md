# TRIZ Engineering Co-Pilot

A systematic innovation assistant powered by TRIZ methodology. Helps engineers solve technical contradictions and generate creative solutions.

## What is TRIZ?

TRIZ (Theory of Inventive Problem Solving) is a proven methodology for systematic innovation, based on patterns from millions of patents. This tool makes TRIZ accessible through AI assistance.

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker (for Qdrant vector database)
- Ollama (for local embeddings)

### 2. Installation

```bash
# Clone and enter directory
cd /path/to/triz2

# Install dependencies
uv sync

# Start services
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
ollama serve
ollama pull nomic-embed-text

# Initialize knowledge base
python src/triz_tools/setup/knowledge_ingestion.py
python src/triz_tools/setup/materials_ingestion.py
```

### 3. Test It

```bash
# Quick test
python src/cli.py solve "Reduce weight while maintaining strength"

# Run validation
python scripts/validate_quickstart.py
```

## How to Use

### Standalone CLI

```bash
# Solve a problem
python src/cli.py solve "Your engineering problem here"

# Start interactive workflow
python src/cli.py workflow start

# Get a specific TRIZ principle
python src/cli.py tool principle 15

# Interactive mode
python src/cli.py interactive
```

### Claude Code Integration

Add TRIZ tools to Claude Code with slash commands:

```bash
# Guided workflow (learning mode)
/triz-workflow "Design a lightweight but strong component"

# Quick autonomous solve
/triz-solve "Reduce noise while increasing airflow"

# Direct tool access
/triz-tool principle 35
```

See [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) for installation instructions.

## Three Ways to Work

### 1. Guided Workflow (Best for Learning)
Step-by-step TRIZ methodology:
- Problem definition
- Contradiction analysis
- Principle selection
- Solution generation

```bash
python src/cli.py workflow start
```

### 2. Autonomous Solve (Best for Speed)
Complete analysis in one go:
- Identifies contradictions
- Recommends principles
- Generates 3-5 solutions
- Suggests materials

```bash
python src/cli.py solve "Your problem description"
```

### 3. Direct Tools (Best for Experts)
Direct access to TRIZ components:
- Look up principles
- Query contradiction matrix
- Search materials database

```bash
python src/cli.py tool principle 15
python src/cli.py tool matrix --improving 1 --worsening 14
```

## TRIZ Components

- **40 Inventive Principles**: Proven patterns for innovation
- **39 Engineering Parameters**: Standard contradiction parameters
- **Contradiction Matrix**: Maps problems to relevant principles
- **Materials Database**: Engineering materials with properties

## Performance

- Tool queries: <2 seconds
- Autonomous solve: <10 seconds
- Memory usage: <1GB
- Fully offline capable

## Troubleshooting

### Services Not Running
```bash
# Check Qdrant
curl http://localhost:6333/health

# Check Ollama
ollama list | grep nomic-embed-text
```

### Reset Knowledge Base
```bash
python src/triz_tools/setup/knowledge_ingestion.py --force
```

### Check System Health
```bash
python -c "from src.triz_tools.health_checks import run_health_check; run_health_check()"
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed setup guide
- [docs/cli_usage.md](docs/cli_usage.md) - Complete CLI reference
- [docs/api_reference.md](docs/api_reference.md) - API documentation
- [CLAUDE.md](CLAUDE.md) - Development guide

## Examples

**Automotive**: "Reduce car weight while maintaining crash safety"
→ Suggests composite materials, honeycomb structures, segmentation principles

**Electronics**: "Improve heat dissipation without increasing size"
→ Recommends phase change materials, heat pipes, dynamic cooling

**Manufacturing**: "Increase production speed without quality loss"
→ Proposes automation, feedback systems, predictive quality control

## Testing

```bash
# Run all tests
pytest tests/ -v

# Specific test categories
pytest tests/contract/ -v      # Contract tests
pytest tests/integration/ -v   # Integration tests
pytest tests/performance/ -v   # Performance tests
```

## Configuration

Set environment variables:
```bash
export TRIZ_QDRANT_HOST=localhost
export TRIZ_QDRANT_PORT=6333
export TRIZ_OLLAMA_HOST=localhost:11434
export TRIZ_LOG_LEVEL=INFO
```

## License

MIT License - See LICENSE file for details.

## Support

- Check system status: `python -m src.triz_tools.health_checks`
- View logs: `tail -f logs/triz.log`
- Run diagnostics: `python scripts/validate_quickstart.py`
