# GEMINI.md

This file provides guidance to Google Gemini CLI when working with the TRIZ Engineering Co-Pilot system.

## Active Technologies
- **TRIZ Methodology**: Theory of Inventive Problem Solving with 40 principles
- **Vector Database**: Qdrant for semantic search of TRIZ knowledge
- **Embeddings**: Ollama with nomic-embed-text-v1.5 for technical content
- **Session Management**: File-based JSON state persistence
- **MCP Server**: Tool integration for structured TRIZ analysis

## TRIZ Core Components

### 40 Inventive Principles
The system contains structured knowledge of all 40 TRIZ inventive principles:
1. Segmentation - Divide objects into parts
2. Taking out - Separate interfering parts
3. Local quality - Heterogeneous structure
4. Asymmetry - Non-symmetric solutions
5. Merging - Combine identical objects
...continuing through to...
40. Composite materials - Multi-material solutions

### 39 Engineering Parameters
Standard TRIZ contradiction analysis uses parameters like:
1. Weight of moving object
2. Weight of stationary object  
3. Length of moving object
4. Length of stationary object
5. Area of moving object
...through to...
39. Productivity

### Contradiction Matrix
39x39 matrix mapping parameter contradictions to recommended principles.
Example: Improving Weight (#1) vs Worsening Strength (#14) → Principles 1, 8, 15, 40

## Project Structure
```
triz-copilot/
├── src/
│   ├── triz_tools/              # Core TRIZ library
│   │   ├── knowledge_base.py    # Vector DB operations
│   │   ├── contradiction_matrix.py  # Matrix lookup
│   │   ├── session_manager.py   # State management
│   │   └── embeddings.py        # Ollama integration
│   └── gemini_extensions/       # Gemini CLI integration
│       └── triz_tool.py         # MCP tool registration
├── data/
│   ├── triz_principles.txt      # 40 principles knowledge
│   ├── contradiction_matrix.json
│   └── materials_database.csv
└── ~/.gemini/commands/triz/     # TOML command definitions
    ├── workflow.toml
    ├── solve.toml
    └── tool.toml
```

## Available Commands

### Phase 1: TOML-based Slash Commands
```bash
# Guided step-by-step TRIZ workflow
gemini /triz:workflow "problem description"

# Autonomous TRIZ analysis and solution generation  
gemini /triz:solve "contradiction or problem statement"

# Direct access to specific TRIZ tools
gemini /triz:tool "analysis requirement"
```

### Phase 2: MCP Server Tools (Advanced)
- `analyze_contradiction`: Technical contradiction analysis
- `generate_solutions`: Solution concept generation
- `function_analysis`: System function modeling
- `get_principle_details`: Principle lookup
- `manage_session`: Session state management

## Workflow Modes

### 1. Guided Workflow Mode (/triz:workflow)
Six-stage systematic process:
1. **Problem Definition**: Problem statement and Ideal Final Result
2. **Function Analysis**: Identify useful and harmful functions  
3. **Contradiction Analysis**: Formulate technical/physical contradictions
4. **Parameter Mapping**: Map to 39 engineering parameters
5. **Principle Selection**: Use contradiction matrix to find principles
6. **Solution Generation**: Apply principles to create solutions
7. **Evaluation**: Assess solutions against IFR and constraints

### 2. Autonomous Solve Mode (/triz:solve)
Single-command complete TRIZ analysis returning:
- Problem summary and IFR identification
- Contradiction analysis results
- Top 3-5 applicable principles with rationale
- 3-5 solution concepts with pros/cons
- Materials recommendations where applicable
- Confidence score for overall analysis

### 3. Direct Tool Mode (/triz:tool)
Expert-level access to specific TRIZ components:
- Principle lookup by number
- Contradiction matrix queries
- Contextual brainstorming with specific principles
- Materials database searches

## Key Data Structures

### Session State (JSON)
```json
{
  "session_id": "uuid",
  "workflow_type": "guided|autonomous|tool", 
  "current_stage": "problem_definition|contradiction_analysis|...",
  "problem_statement": "user input",
  "ideal_final_result": "desired outcome",
  "contradictions": [{"improving": 1, "worsening": 14}],
  "selected_principles": [1, 15, 40],
  "solution_concepts": [...],
  "materials_recommendations": [...]
}
```

### Solution Concept Structure
```json
{
  "concept_title": "Descriptive name",
  "description": "Detailed explanation",
  "applied_principles": [1, 15],
  "principle_applications": "How principles were used",
  "pros": ["advantage 1", "advantage 2"],
  "cons": ["limitation 1", "limitation 2"], 
  "feasibility_score": 0.85,
  "innovation_level": 3,
  "materials_suggested": ["CFRP", "Ti-6Al-4V"]
}
```

## Technical Implementation

### Vector Database (Qdrant)
- **Collections**: triz_principles, materials_database, solution_case_studies
- **Embeddings**: 768D vectors for detailed content, 384D for summaries
- **Distance Metric**: Cosine similarity for semantic search
- **Indexing**: Payload indexes on principle_number, domains, industry

### Embedding Strategy
- **Primary Model**: nomic-embed-text-v1.5 (768D, 8192 token context)
- **Performance Mode**: 256D vectors (1% accuracy loss, 66% memory savings)
- **Local Processing**: Ollama on macOS M4 with optimization flags
- **Caching**: Pre-computed embeddings for all 40 principles

### Performance Targets
- **Tool Queries**: <2 seconds response time
- **Autonomous Solve**: <10 seconds complete analysis
- **Memory Usage**: <1GB total footprint
- **Embedding Generation**: 60+ tokens/second on M4

## Integration Patterns

### Command Processing Flow
1. User input → Gemini CLI parser
2. TOML/MCP command routing → TRIZ tool selection
3. Python function execution → Vector database queries
4. TRIZ logic application → Solution generation
5. Response formatting → Structured output to CLI

### Error Handling
- Validate principle numbers (1-40 range)
- Verify parameter IDs (1-39 range) 
- Handle Qdrant connection failures gracefully
- Provide fallback for missing embeddings
- Clear error messages with corrective suggestions

### Session Management
- File-based persistence in `~/.triz_sessions/`
- Automatic session creation and state tracking
- Cross-invocation continuity for guided workflows
- Session reset and cleanup capabilities

## Development Guidelines

### Constitutional Compliance
- **Library-First**: Core TRIZ logic in standalone `triz_tools` library
- **CLI Integration**: Minimal changes to Gemini CLI codebase
- **Test-First**: Contract tests before implementation
- **Local-First**: No cloud dependencies, offline capable
- **Performance**: Meet response time requirements

### Code Patterns
```python
# Tool function signature
def triz_tool_function(params: Dict) -> TRIZToolResponse:
    """TRIZ tool with standard response format"""
    return TRIZToolResponse(
        success=bool,
        message=str,
        data=dict,
        session_id=str
    )

# Vector search pattern
def search_principles(query: str, top_k: int = 5) -> List[Dict]:
    """Semantic search in TRIZ knowledge base"""
    vector = embedding_model.encode(query)
    results = qdrant_client.search(
        collection_name="triz_principles",
        query_vector=vector,
        limit=top_k
    )
    return results
```

## Recent Changes
- Initial TRIZ Engineering Co-Pilot implementation
- Integrated Qdrant vector database with TRIZ knowledge
- Added Ollama embedding support for macOS M4
- Implemented session-based workflow state management
- Created MCP server for advanced tool integration
- Added comprehensive TRIZ principle and contradiction matrix knowledge

## Usage Examples

### Problem: Lightweight but strong automotive component
```bash
# Guided learning approach
gemini /triz:workflow "Design lightweight but strong automotive component for electric vehicle"

# Expert quick analysis  
gemini /triz:solve "Reduce component weight by 30% while maintaining crash safety requirements"

# Specific tool usage
gemini /triz:tool "Apply segmentation principle to brake disc design"
```

### Expected TRIZ Analysis Output
- **Contradiction**: Weight (#1) vs Strength (#14)
- **Principles**: Segmentation, Composite materials, Dynamics
- **Solutions**: Hollow structures, composite materials, topology optimization
- **Materials**: Carbon fiber, aluminum alloys, advanced steels

This TRIZ Co-Pilot transforms systematic innovation methodology into an accessible, intelligent assistant integrated seamlessly with the Gemini CLI environment.