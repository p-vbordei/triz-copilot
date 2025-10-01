# Quickstart: Claude CLI with TRIZ Co-Pilot

## Prerequisites

- Python 3.11+ installed
- Claude CLI installed and configured
- Docker (for Qdrant vector database)
- 2GB free disk space

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd triz2

# Install dependencies
uv sync
uv add anthropic-mcp  # Claude integration

# Start required services
docker-compose up -d  # Starts Qdrant on port 6333
ollama serve         # Start Ollama service
ollama pull nomic-embed-text  # Download embedding model
```

### 2. Configure Claude CLI

```bash
# Run the setup script
./scripts/setup-claude.sh

# Or manually configure:
mkdir -p ~/.claude/mcp
cp claude-mcp-manifest.json ~/.claude/mcp/triz-copilot.json

# Verify installation
claude mcp list
# Should show: triz-copilot
```

### 3. Initialize Knowledge Base

```bash
# First time setup - ingest TRIZ knowledge
python src/triz_tools/setup/knowledge_ingestion.py
python src/triz_tools/setup/materials_ingestion.py

# Verify vector database
curl http://localhost:6333/collections
# Should show: triz_principles, triz_materials
```

## Basic Usage

### Starting Claude with TRIZ

```bash
# Start Claude CLI
claude chat

# Verify TRIZ commands are available
> /help
# Should list: /triz-workflow, /triz-solve, /triz-tool
```

### Guided Workflow Mode

Perfect for learning TRIZ methodology:

```
> /triz-workflow

🔧 TRIZ Engineering Co-Pilot - Guided Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1 of 6: Problem Definition
Please describe your engineering problem and the Ideal Final Result (IFR).

> I need to reduce the weight of a drone while maintaining its strength

✅ Problem captured. 

Step 2 of 6: Function & Contradiction Analysis
What is improving and what is getting worse?

> Weight is improving but structural integrity is getting worse

[Continue through all 6 steps...]
```

### Autonomous Solve Mode

For experienced users who want quick analysis:

```
> /triz-solve reduce vibration in high-speed motor without adding dampers

🔍 Analyzing problem...

## TRIZ Analysis Report

### Problem Summary
Reduce vibration in high-speed motor without adding damping components

### Key Contradictions Identified
1. Technical: Speed vs Vibration
2. Physical: Motor must be fast AND stable

### Recommended Principles
1. **Principle 2 - Taking Out**: Separate disturbing parts
2. **Principle 35 - Parameter Changes**: Change physical state
3. **Principle 18 - Mechanical Vibration**: Use resonance

### Solution Concepts
1. **Active Vibration Cancellation**
   - Use counter-rotating masses
   - Applies: Principle 2
   
2. **Resonance Tuning**
   - Adjust natural frequency away from operating speed
   - Applies: Principle 18

[Session ID: abc-123-def]
```

### Direct Tool Access

For expert users who know exactly what they need:

```
# Get a specific principle
> /triz-tool get-principle 15

## Principle 15: Dynamics
a) Make objects adaptive to varying conditions
b) Divide object into parts capable of movement
c) If rigid, make movable or adaptive

Examples:
- Flexible manufacturing systems
- Adjustable steering wheels
- Adaptive algorithms

# Use contradiction matrix
> /triz-tool contradiction-matrix --improving 2 --worsening 14

Improving: Weight of moving object
Worsening: Strength

Recommended Principles: 1, 8, 15, 40

# Brainstorm with context
> /triz-tool brainstorm --principle 35 --context "battery thermal management"

## Brainstorming: Principle 35 (Parameter Changes)
Context: battery thermal management

Ideas:
1. Phase-change materials for passive cooling
2. Liquid-to-gas coolant systems
3. Reversible chemical reactions for heat absorption
```

## Working with Sessions

### Continue Previous Session

```
> /triz-workflow continue abc-123-def

📂 Resuming session abc-123-def
Currently at Step 4 of 6: Principle Identification

[Continue where you left off...]
```

### Cross-Platform Sessions

Start in Claude, continue in Gemini:

```bash
# In Claude
> /triz-workflow
[Work through steps 1-3]
Session ID: xyz-789

# In Gemini CLI
> gemini triz continue xyz-789
[Continue from step 4]
```

## Advanced Features

### Custom Context

```
> /triz-solve --industry aerospace --constraints "no weight increase, $10k budget" \
  improve fuel efficiency of small aircraft engine
```

### Batch Analysis

```bash
# Create problems file
cat > problems.txt << EOF
reduce noise in vacuum cleaner
increase battery life without size increase
prevent ice formation on wings
EOF

# Run batch analysis
python scripts/batch_triz.py problems.txt --platform claude
```

### Export Results

```
> /triz-solve vibration problem
[Analysis completes]

> /export-session abc-123 --format pdf
📄 Exported to: ~/triz-reports/abc-123-analysis.pdf
```

## Troubleshooting

### Command Not Found

```
Error: Command /triz-workflow not recognized
```

**Solution**: Restart Claude CLI, run `./scripts/setup-claude.sh`

### Vector Database Connection Failed

```
Error: Cannot connect to Qdrant at localhost:6333
```

**Solution**: 
```bash
docker ps  # Check if Qdrant is running
docker-compose up -d  # Start services
```

### Embedding Model Not Found

```
Error: Ollama model 'nomic-embed-text' not found
```

**Solution**:
```bash
ollama pull nomic-embed-text
ollama list  # Verify model is downloaded
```

### Session Not Found

```
Error: Session xyz-789 not found or expired
```

**Solution**: Sessions expire after 24 hours. Start a new session.

## Configuration

### Customize Settings

Edit `~/.triz/config/claude.json`:

```json
{
  "session_timeout_hours": 48,  // Extend session lifetime
  "default_language": "en",
  "response_style": "detailed",  // or "concise"
  "auto_save": true
}
```

### Performance Tuning

```bash
# Increase vector search results
export TRIZ_VECTOR_TOP_K=10  # Default: 5

# Enable debug logging
export TRIZ_LOG_LEVEL=DEBUG

# Use GPU for embeddings (if available)
export OLLAMA_GPU=true
```

## Examples Repository

Find more examples at:
- `examples/claude/` - Claude-specific examples
- `examples/workflows/` - Complete workflow sessions
- `examples/solutions/` - Real problem solutions

## Getting Help

```
# In Claude CLI
> /triz-help

# View documentation
> /triz-docs contradiction-matrix

# Report issues
> /triz-feedback "Issue description"
```

## Next Steps

1. Try the [Interactive Tutorial](./tutorials/01-basics.md)
2. Read [TRIZ Principles Guide](./docs/principles.md)
3. Explore [Case Studies](./examples/case-studies/)
4. Join [TRIZ Community Discord](#)

---

**Quick Reference Card**

| Command | Purpose | Example |
|---------|---------|---------|
| `/triz-workflow` | Start guided process | `/triz-workflow` |
| `/triz-solve` | Quick analysis | `/triz-solve reduce weight` |
| `/triz-tool get-principle N` | View principle | `/triz-tool get-principle 35` |
| `/triz-tool contradiction-matrix` | Matrix lookup | `/triz-tool contradiction-matrix --improving 1 --worsening 2` |
| `/triz-tool brainstorm` | Generate ideas | `/triz-tool brainstorm --principle 15 --context "robotics"` |
| `/triz-workflow continue ID` | Resume session | `/triz-workflow continue abc-123` |