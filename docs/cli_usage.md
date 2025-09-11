# CLI Usage Guide

This guide covers how to use the TRIZ Engineering Co-Pilot through various interfaces including the command line, Gemini CLI integration, and MCP server.

## Table of Contents

- [Installation](#installation)
- [Command Line Interface](#command-line-interface)
- [Gemini CLI Integration](#gemini-cli-integration)
- [MCP Server](#mcp-server)
- [Workflow Modes](#workflow-modes)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- Ollama (for embeddings)

### Setup

1. **Install dependencies:**
   ```bash
   cd /path/to/triz2
   pip install -e .
   ```

2. **Start infrastructure services:**
   ```bash
   # Start Qdrant vector database
   docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
   
   # Start Ollama and pull embedding model
   ollama serve
   ollama pull nomic-embed-text
   ```

3. **Initialize knowledge base:**
   ```bash
   python -m src.triz_tools.setup.knowledge_ingestion
   python -m src.triz_tools.setup.matrix_loader
   ```

## Command Line Interface

### Basic Commands

```bash
# Direct CLI usage
python -m src.cli --help

# Run health checks
python -m src.cli health

# Load knowledge base
python -m src.cli load-knowledge

# Start interactive session
python -m src.cli interactive
```

### Tool Functions

```bash
# Get TRIZ principle information
python -c "from src.triz_tools.direct_tools import triz_tool_get_principle; print(triz_tool_get_principle(1))"

# Look up contradiction matrix
python -c "from src.triz_tools.direct_tools import triz_tool_contradiction_matrix; print(triz_tool_contradiction_matrix(1, 14))"

# Autonomous problem solving
python -c "from src.triz_tools.solve_tools import triz_solve_autonomous; print(triz_solve_autonomous('Reduce weight while maintaining strength'))"
```

## Gemini CLI Integration

### Setup Gemini CLI

1. **Install Gemini CLI** (follow official documentation)

2. **Configure TRIZ tools:**
   ```bash
   # Copy configuration
   cp gemini-cli-config.toml ~/.config/gemini-cli/
   ```

3. **Start MCP server:**
   ```bash
   python src/mcp_server.py
   ```

### Available Commands

#### Guided Workflow Mode

Step-by-step TRIZ methodology for learning users:

```bash
# Start new problem-solving session
gemini /triz-workflow "Design lightweight but strong automotive component"

# Continue workflow
gemini /triz-workflow-continue "Component has zero weight but infinite strength" --session-id abc123

# Reset workflow
gemini /triz-workflow-reset --session-id abc123

# Check workflow status
gemini /triz-workflow-status --session-id abc123
```

#### Autonomous Solve Mode

Complete problem analysis for experienced users:

```bash
# Solve problem autonomously
gemini /triz-solve "Reduce aircraft wing weight while maintaining structural strength"

# Solve with context
gemini /triz-solve "Improve heat dissipation" --context "electronics, passive cooling preferred"

# Iterative solving
gemini /triz-solve-iterative "Reduce vibration" --iteration 2 --feedback "Focus on passive solutions"
```

#### Direct Tool Mode

Expert access to specific TRIZ components:

```bash
# Get principle information
gemini /triz-tool get-principle 15

# Contradiction matrix lookup
gemini /triz-tool contradiction-matrix --improving 1 --worsening 14

# Brainstorm solutions
gemini /triz-tool brainstorm --principle 40 --context "Solar panel efficiency"

# Materials recommendation
gemini /triz-tool materials --requirements "lightweight, high-strength, heat-resistant"
```

## MCP Server

### Starting the Server

```bash
# Start with default settings
python src/mcp_server.py

# Start with custom port
python src/mcp_server.py --port 8080

# Start with debug logging
python src/mcp_server.py --debug
```

### Server Configuration

The MCP server provides the following tools:

- `triz_workflow_start` - Start guided workflow
- `triz_workflow_continue` - Continue workflow step
- `triz_solve_autonomous` - Autonomous problem solving
- `triz_tool_get_principle` - Get principle information
- `triz_tool_contradiction_matrix` - Matrix lookup
- `triz_tool_brainstorm` - Generate solutions

### Client Integration

Example Python client:

```python
import json
import requests

# Connect to MCP server
server_url = "http://localhost:3000"

# Start workflow
response = requests.post(f"{server_url}/tools/triz_workflow_start", 
                        json={"arguments": {}})
result = response.json()
session_id = result["session_id"]

# Continue workflow
response = requests.post(f"{server_url}/tools/triz_workflow_continue",
                        json={
                            "arguments": {
                                "session_id": session_id,
                                "user_input": "Design a lightweight strong component"
                            }
                        })
```

## Workflow Modes

### 1. Guided Workflow Mode

**Best for:** Learning TRIZ, systematic approach, complex problems

**Steps:**
1. Problem Definition
2. Ideal Final Result (IFR)
3. Contradiction Analysis
4. Principle Selection
5. Solution Generation
6. Evaluation

**Example:**
```bash
gemini /triz-workflow "Our manufacturing system needs faster production without quality loss"
# System guides through each step...
```

### 2. Autonomous Solve Mode

**Best for:** Experienced users, quick analysis, known problem types

**Features:**
- Complete analysis in one call
- Multiple solution concepts
- Feasibility scoring
- Material recommendations

**Example:**
```bash
gemini /triz-solve "Electric vehicle battery needs longer range with faster charging"
```

### 3. Direct Tool Mode

**Best for:** Experts, specific lookups, integration with other tools

**Tools:**
- Principle lookup by ID
- Contradiction matrix queries
- Context-aware brainstorming
- Materials database search

**Example:**
```bash
gemini /triz-tool get-principle 35  # Parameter changes
gemini /triz-tool contradiction-matrix --improving 21 --worsening 25
```

## Examples

### Example 1: Automotive Weight Reduction

```bash
# Guided approach
gemini /triz-workflow "Reduce car weight while maintaining crash safety"

# Expected flow:
# 1. Problem: "Reduce car weight while maintaining crash safety"
# 2. IFR: "Car has zero weight but perfect crash protection"
# 3. Contradiction: Weight (1) vs Strength (14)
# 4. Principles: [1, 8, 15, 40] (Segmentation, Composite materials, etc.)
# 5. Solutions: Honeycomb structures, advanced composites, modular design
```

### Example 2: Manufacturing Efficiency

```bash
# Autonomous approach
gemini /triz-solve "Increase production speed by 50% while reducing defects from 3% to 0.5%"

# Response includes:
# - Contradictions identified: Speed vs Quality
# - Recommended principles: Dynamics, Automation, Feedback
# - Solution concepts with feasibility scores
# - Implementation suggestions
```

### Example 3: Electronics Cooling

```bash
# Direct tool approach
gemini /triz-tool contradiction-matrix --improving 22 --worsening 30
# Returns: Principles [2, 14, 15, 35] for Energy vs Harmful factors

gemini /triz-tool brainstorm --principle 2 --context "Passive cooling for smartphones"
# Returns: Specific solutions using "Taking out" principle
```

### Example 4: Materials Selection

```bash
# Materials recommendation
gemini /triz-tool materials --requirements "lightweight, conductive, flexible"

# Returns:
# - Carbon nanotubes (high performance)
# - Graphene composites (emerging)
# - Conductive polymers (cost-effective)
# - With properties and applications
```

## Advanced Usage

### Session Management

```python
from src.triz_tools.session_manager import get_session_manager

# Create and manage sessions
manager = get_session_manager()
session_id = manager.create_session()

# Save progress
manager.save_problem_statement(session_id, "My problem")
manager.save_contradictions(session_id, [{"improving": 1, "worsening": 14}])

# Export session
manager.export_session(session_id, "my_session.json")
```

### Batch Processing

```python
from src.triz_tools.solve_tools import triz_solve_autonomous

problems = [
    "Reduce energy consumption",
    "Improve user experience", 
    "Increase reliability"
]

results = []
for problem in problems:
    result = triz_solve_autonomous(problem)
    results.append(result)
```

### Custom Analysis

```python
from src.triz_tools.services.analysis_service import get_analysis_service
from src.triz_tools.knowledge_base import get_knowledge_base

analysis = get_analysis_service()
kb = get_knowledge_base()

# Custom contradiction analysis
contradictions = analysis.identify_contradictions("Speed vs accuracy problem")
principles = analysis.recommend_principles(contradictions)
solutions = analysis.generate_solutions(principles, "robotics context")
```

## Performance Tuning

### Caching

```python
# Enable embedding cache
from src.triz_tools.embeddings import get_embedding_client

client = get_embedding_client()
client.enable_cache(cache_size=1000, ttl_hours=24)
```

### Vector Database Optimization

```bash
# Optimize Qdrant settings
docker run -d -p 6333:6333 -p 6334:6334 \
  -e QDRANT__SERVICE__MAX_REQUEST_SIZE_MB=32 \
  -e QDRANT__SERVICE__MAX_CONCURRENT_REQUESTS=10 \
  qdrant/qdrant
```

## Configuration

### Environment Variables

```bash
# Vector database
export TRIZ_QDRANT_HOST=localhost
export TRIZ_QDRANT_PORT=6333

# Embeddings
export TRIZ_OLLAMA_HOST=localhost:11434
export TRIZ_EMBEDDING_MODEL=nomic-embed-text

# Storage
export TRIZ_DATA_DIR=./data
export TRIZ_CACHE_DIR=./cache
export TRIZ_SESSION_DIR=./sessions

# Logging
export TRIZ_LOG_LEVEL=INFO
export TRIZ_LOG_FORMAT=json
```

### Configuration File

Create `config.json`:

```json
{
  "database": {
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "use_memory_storage": false
  },
  "embedding": {
    "model_name": "nomic-embed-text",
    "dimension": 768,
    "cache_enabled": true
  },
  "session": {
    "storage_dir": "./sessions",
    "auto_save": true,
    "cleanup_days": 30
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Qdrant Connection Failed

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Restart Qdrant
docker restart $(docker ps -q --filter ancestor=qdrant/qdrant)
```

#### 2. Ollama Model Not Found

```bash
# Pull required model
ollama pull nomic-embed-text

# List available models
ollama list
```

#### 3. Empty Knowledge Base

```bash
# Reinitialize knowledge base
python -m src.triz_tools.setup.knowledge_ingestion --force
python -m src.triz_tools.setup.matrix_loader --reload
```

#### 4. Session Not Found

```python
# List active sessions
from src.triz_tools.session_manager import get_session_manager
manager = get_session_manager()
sessions = manager.list_sessions()
print(f"Active sessions: {len(sessions)}")
```

#### 5. Performance Issues

```bash
# Run performance diagnostics
python -m src.triz_tools.health_checks --performance

# Enable debug logging
export TRIZ_LOG_LEVEL=DEBUG
```

### Debug Mode

```bash
# Enable debug logging
export TRIZ_DEBUG=true

# Run with verbose output
python -m src.cli --verbose

# Check system health
python -c "from src.triz_tools.health_checks import run_health_check; print(run_health_check())"
```

### Getting Help

1. **Check system status:**
   ```bash
   python -m src.triz_tools.health_checks
   ```

2. **View logs:**
   ```bash
   tail -f logs/triz.log
   ```

3. **Test basic functionality:**
   ```bash
   python -c "from src.triz_tools.direct_tools import triz_tool_get_principle; print(triz_tool_get_principle(1)['success'])"
   ```

## Integration Examples

### Jupyter Notebook

```python
import sys
sys.path.append('/path/to/triz2/src')

from triz_tools.solve_tools import triz_solve_autonomous
from triz_tools.direct_tools import triz_tool_get_principle

# Solve problem
result = triz_solve_autonomous("Improve solar panel efficiency")
print(f"Found {len(result['analysis']['solutions'])} solutions")

# Display solutions
for i, solution in enumerate(result['analysis']['solutions']):
    print(f"\n{i+1}. {solution['concept']}")
    print(f"   Feasibility: {solution['feasibility']}")
```

### Web API

```python
from flask import Flask, request, jsonify
from src.triz_tools.solve_tools import triz_solve_autonomous

app = Flask(__name__)

@app.route('/solve', methods=['POST'])
def solve_problem():
    problem = request.json['problem']
    result = triz_solve_autonomous(problem)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### Slack Bot

```python
from slack_bolt import App
from src.triz_tools.solve_tools import triz_solve_autonomous

app = App(token="your-token")

@app.message("solve:")
def handle_solve(message, say):
    problem = message['text'].replace('solve:', '').strip()
    result = triz_solve_autonomous(problem)
    
    solutions = result['analysis']['solutions'][:3]  # Top 3
    response = f"🔧 TRIZ Solutions for: {problem}\n\n"
    
    for i, sol in enumerate(solutions):
        response += f"{i+1}. {sol['concept']} (Score: {sol['feasibility']})\n"
    
    say(response)

app.start(port=3000)
```

## Best Practices

1. **Always check health status** before starting work
2. **Use appropriate mode** for your use case and experience level
3. **Save sessions** for complex problems you'll revisit
4. **Enable caching** for better performance
5. **Monitor resource usage** with concurrent requests
6. **Regular cleanup** of old sessions and cache
7. **Use structured logging** for debugging

## Performance Benchmarks

- **Tool queries:** < 2 seconds (target)
- **Autonomous solve:** < 10 seconds (target) 
- **Memory usage:** < 1GB (typical)
- **Concurrent users:** 5-10 (recommended)

This completes the CLI usage guide. The system provides flexible access through multiple interfaces while maintaining the core TRIZ methodology and performance requirements.