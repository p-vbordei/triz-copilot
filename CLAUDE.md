# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The TRIZ Engineering Co-Pilot is a complete implementation of the Theory of Inventive Problem Solving (TRIZ) methodology as an intelligent assistant. It extends Google Gemini CLI with systematic innovation capabilities and provides three main interaction modes:

- **Guided Workflow Mode** (`/triz-workflow`): Step-by-step TRIZ methodology for learning users
- **Autonomous Solve Mode** (`/triz-solve`): Complete problem analysis for experienced users  
- **Direct Tool Mode** (`/triz-tool`): Expert access to specific TRIZ components

## Architecture

### Core Technology Stack
- **Python 3.11+** with uv package manager
- **Qdrant Vector Database**: Local semantic search (Docker container on port 6333)
- **Ollama**: Local embeddings with nomic-embed-text model
- **MCP Server**: Tool integration with Gemini CLI
- **JSON**: Session state persistence

### High-Level Architecture

The system follows a library-first approach with three main layers:

1. **Core TRIZ Library** (`src/triz_tools/`): Standalone Python library implementing all TRIZ logic, vector operations, and session management
2. **CLI Integration** (`src/cli.py`, `src/mcp_server.py`): Minimal wrapper for Gemini CLI and standalone CLI usage
3. **Data Layer** (`src/data/`): TRIZ knowledge base, contradiction matrix, and materials database

Key architectural patterns:
- **Vector Search**: Semantic similarity search using Qdrant for finding relevant TRIZ principles and materials
- **Session Management**: JSON-based state persistence for multi-step workflows
- **Service Pattern**: Separated services for embeddings, vector operations, session management, and analysis
- **Fallback Strategy**: File-based alternatives when Qdrant/Ollama unavailable

## Common Development Commands

### Build and Setup
```bash
# Install dependencies with uv
uv sync

# Start required services
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
ollama serve
ollama pull nomic-embed-text

# Initialize knowledge base (first time setup)
python src/triz_tools/setup/knowledge_ingestion.py
python src/triz_tools/setup/materials_ingestion.py
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/contract/ -v          # Contract tests (TDD)
pytest tests/integration/ -v       # Integration tests
pytest tests/unit/ -v              # Unit tests
pytest tests/performance/ -v       # Performance tests

# Run a single test file
pytest tests/contract/test_workflow_contract_green.py -v

# Validate quickstart scenarios
python scripts/validate_quickstart.py
```

### Running the Application
```bash
# Standalone CLI mode
python src/cli.py solve "Your engineering problem here"
python src/cli.py workflow start
python src/cli.py tool principle 15

# Interactive mode
python src/cli.py interactive

# Test individual tools
python test_triz.py              # Test basic TRIZ functionality
python test_embeddings.py         # Test embedding generation
```

### Linting and Type Checking
```bash
# Format code with black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Type checking with mypy (if configured)
mypy src/
```

## TRIZ-Specific Code Patterns

### Working with TRIZ Tools

The three main tool modules follow consistent patterns:

```python
# Workflow tools (src/triz_tools/workflow_tools.py)
response = triz_workflow_start()
response = triz_workflow_continue(session_id, user_input)

# Solve tools (src/triz_tools/solve_tools.py)  
response = triz_solve_autonomous(problem_description)

# Direct tools (src/triz_tools/direct_tools.py)
response = triz_tool_get_principle(principle_number)
response = triz_tool_contradiction_matrix(improving, worsening)
```

All responses follow the `TRIZToolResponse` structure with success, message, data, session_id, and stage fields.

### Vector Search Operations

When implementing new search features:

```python
from src.triz_tools.services.vector_service import VectorService

# Search for relevant principles
service = VectorService()
results = service.search_principles(query_text, top_k=5)

# Fallback to file-based search if Qdrant unavailable
from src.triz_tools.services.file_vector_service import FileVectorService
fallback = FileVectorService()
```

### Session Management

For stateful workflows:

```python
from src.triz_tools.session_manager import SessionManager

manager = SessionManager()
session = manager.create_session()
manager.update_session(session_id, stage="contradiction_analysis", data={})
session = manager.get_session(session_id)
```

## Key Implementation Details

### TRIZ Knowledge Base
- 40 inventive principles with examples and sub-principles
- 39x39 contradiction matrix mapping parameters to principles
- Materials database with engineering properties
- All data in `src/data/` directory with JSON/CSV formats

### Performance Targets
- Tool queries: <2 seconds response time
- Autonomous solve: <10 seconds for complete analysis
- Memory usage: <1GB total footprint
- Embedding generation: 60+ tokens/second on M4

### Error Handling
- Input validation in `src/triz_tools/validation.py`
- Structured logging via `src/triz_tools/logging_config.py`
- Health checks in `src/triz_tools/health_checks.py`
- Graceful fallbacks when external services unavailable

## Testing Strategy

The project follows Test-Driven Development (TDD) with RED-GREEN-Refactor:

1. **Contract Tests First**: Define tool interfaces and expected behavior
2. **Integration Tests**: Verify service interactions and workflows
3. **Unit Tests Last**: Test individual functions after implementation

Key test files:
- `tests/contract/test_*_contract_green.py`: Passing contract tests
- `tests/integration/test_full_workflow.py`: End-to-end workflow validation
- `tests/performance/test_response_times.py`: Performance benchmarks

## Current Status

✅ **IMPLEMENTATION COMPLETE** - All 63 tasks completed:
- Core TRIZ library with 40 principles and contradiction matrix
- Vector search with Qdrant and file-based fallback
- Session management with JSON persistence
- CLI and MCP server integration
- Comprehensive test coverage (contract, integration, unit, performance)
- Documentation and quickstart guide

The system is production-ready and successfully transforms TRIZ methodology into an accessible, intelligent assistant.

## Active Development

🚧 **Feature Branch: 002-add-claude-cli**
- Adding Claude CLI integration alongside existing Gemini CLI support
- Implementing `/triz-workflow`, `/triz-solve`, and `/triz-tool` commands for Claude
- Ensuring platform-agnostic session management
- Specification complete, awaiting implementation plan