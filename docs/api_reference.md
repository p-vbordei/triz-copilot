# API Reference

This document provides comprehensive API reference for the TRIZ Engineering Co-Pilot system.

## Table of Contents

- [Tool Functions](#tool-functions)
- [Workflow Functions](#workflow-functions)
- [Core Services](#core-services)
- [Data Models](#data-models)
- [Utilities](#utilities)
- [Configuration](#configuration)
- [Error Handling](#error-handling)

## Tool Functions

### Direct Tools (`src.triz_tools.direct_tools`)

#### `triz_tool_get_principle(principle_number: int) -> Dict[str, Any]`

Retrieve information about a specific TRIZ principle.

**Parameters:**
- `principle_number` (int): Principle ID (1-40)

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "data": {
        "id": int,
        "name": str,
        "description": str,
        "examples": List[str],
        "applications": List[str],
        "related_principles": List[int]
    },
    "session_id": Optional[str],
    "stage": Optional[str]
}
```

**Example:**
```python
from src.triz_tools.direct_tools import triz_tool_get_principle

result = triz_tool_get_principle(1)
print(result["data"]["name"])  # "Segmentation"
```

#### `triz_tool_contradiction_matrix(improving: int, worsening: int) -> Dict[str, Any]`

Look up contradiction matrix for parameter pairs.

**Parameters:**
- `improving` (int): Improving parameter ID (1-39)
- `worsening` (int): Worsening parameter ID (1-39)

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "data": {
        "improving_parameter": int,
        "worsening_parameter": int,
        "recommended_principles": List[int],
        "confidence": float
    }
}
```

**Example:**
```python
result = triz_tool_contradiction_matrix(1, 14)  # Weight vs Strength
principles = result["data"]["recommended_principles"]  # [1, 8, 15, 40]
```

#### `triz_tool_brainstorm(principle: int, context: str) -> Dict[str, Any]`

Generate context-specific solutions using a TRIZ principle.

**Parameters:**
- `principle` (int): TRIZ principle ID (1-40)
- `context` (str): Problem context or domain

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "data": {
        "principle": {
            "id": int,
            "name": str,
            "description": str
        },
        "context": str,
        "solutions": List[{
            "concept": str,
            "description": str,
            "feasibility": float,
            "implementation": str
        }]
    }
}
```

**Example:**
```python
result = triz_tool_brainstorm(40, "lightweight automotive components")
solutions = result["data"]["solutions"]
```

#### `triz_tool_materials(requirements: str) -> Dict[str, Any]`

Recommend materials based on requirements.

**Parameters:**
- `requirements` (str): Material requirements description

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "data": {
        "requirements": str,
        "materials": List[{
            "name": str,
            "properties": Dict[str, Any],
            "applications": List[str],
            "advantages": List[str],
            "limitations": List[str],
            "cost_level": str
        }]
    }
}
```

### Solve Tools (`src.triz_tools.solve_tools`)

#### `triz_solve_autonomous(problem: str, context: Optional[Dict] = None) -> Dict[str, Any]`

Perform complete autonomous TRIZ analysis.

**Parameters:**
- `problem` (str): Problem statement
- `context` (Optional[Dict]): Additional context

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "analysis": {
        "problem_statement": str,
        "ideal_final_result": str,
        "contradictions": List[Dict],
        "principles": List[int],
        "solutions": List[{
            "concept": str,
            "principle_id": int,
            "feasibility": float,
            "innovation_level": float,
            "description": str,
            "implementation": str
        }],
        "materials": Optional[List[Dict]],
        "evaluation": Dict[str, Any]
    }
}
```

**Example:**
```python
from src.triz_tools.solve_tools import triz_solve_autonomous

result = triz_solve_autonomous("Reduce weight while maintaining strength")
solutions = result["analysis"]["solutions"]
```

#### `triz_solve_with_context(problem: str, context: Dict[str, Any]) -> Dict[str, Any]`

Solve problem with additional context information.

**Parameters:**
- `problem` (str): Problem statement
- `context` (Dict): Context including industry, constraints, current solutions

**Example:**
```python
context = {
    "industry": "aerospace",
    "constraints": ["cost-effective", "regulatory compliance"],
    "current_solution": "aluminum frame",
    "performance_targets": {"weight_reduction": 30, "strength_maintained": 100}
}

result = triz_solve_with_context("Lightweight aircraft component", context)
```

#### `triz_solve_iterative(problem: str, iteration: int, previous_solutions: List[Dict], feedback: Optional[str] = None) -> Dict[str, Any]`

Iteratively refine solutions based on feedback.

**Parameters:**
- `problem` (str): Problem statement
- `iteration` (int): Iteration number
- `previous_solutions` (List[Dict]): Previous solution concepts
- `feedback` (Optional[str]): Feedback for refinement

### Workflow Tools (`src.triz_tools.workflow_tools`)

#### `triz_workflow_start() -> Dict[str, Any]`

Start a new guided TRIZ workflow session.

**Returns:**
```python
{
    "success": bool,
    "session_id": str,
    "stage": str,
    "message": str,
    "next_step": str,
    "guidance": str
}
```

#### `triz_workflow_continue(session_id: str, user_input: str) -> Dict[str, Any]`

Continue workflow with user input.

**Parameters:**
- `session_id` (str): Session identifier
- `user_input` (str): User's input for current stage

**Returns:**
```python
{
    "success": bool,
    "session_id": str,
    "stage": str,
    "message": str,
    "next_step": Optional[str],
    "data": Dict[str, Any],  # Stage-specific data
    "guidance": str
}
```

#### `triz_workflow_reset(session_id: str) -> Dict[str, Any]`

Reset workflow session to initial state.

#### `triz_workflow_status(session_id: str) -> Dict[str, Any]`

Get current workflow status and progress.

## Core Services

### Knowledge Base (`src.triz_tools.knowledge_base`)

#### `class TRIZKnowledgeBase`

Core knowledge base for TRIZ principles and data.

**Methods:**

##### `add_principle(principle: TRIZPrinciple) -> bool`

Add a TRIZ principle to the knowledge base.

##### `get_principle(principle_id: int) -> Optional[TRIZPrinciple]`

Retrieve principle by ID.

##### `search_principles(query: str, limit: int = 10) -> List[SearchResult]`

Search principles by keyword with relevance scoring.

##### `get_all_principles() -> List[TRIZPrinciple]`

Get all principles sorted by ID.

##### `save() -> bool`

Persist knowledge base to storage.

##### `load() -> bool`

Load knowledge base from storage.

##### `export_to_json(file_path: Path) -> bool`

Export knowledge base to JSON file.

##### `import_from_json(file_path: Path) -> int`

Import principles from JSON file.

**Usage:**
```python
from src.triz_tools.knowledge_base import get_knowledge_base

kb = get_knowledge_base()
principle = kb.get_principle(1)
results = kb.search_principles("segmentation")
```

### Contradiction Matrix (`src.triz_tools.contradiction_matrix`)

#### `class ContradictionMatrix`

TRIZ contradiction matrix for parameter conflicts.

**Methods:**

##### `add_parameter(param_id: int, name: str, description: str) -> bool`

Add engineering parameter.

##### `add_entry(improving: int, worsening: int, principles: List[int]) -> bool`

Add matrix entry for parameter pair.

##### `lookup(improving: int, worsening: int) -> Optional[MatrixEntry]`

Look up recommended principles for contradiction.

##### `get_parameter(param_id: int) -> Optional[EngineeringParameter]`

Get parameter information.

##### `find_parameters_by_keyword(keyword: str) -> List[EngineeringParameter]`

Search parameters by keyword.

##### `load_standard_matrix() -> int`

Load standard 39x39 TRIZ matrix.

**Usage:**
```python
from src.triz_tools.contradiction_matrix import get_matrix_lookup

matrix = get_matrix_lookup()
result = matrix.lookup(1, 14)  # Weight vs Strength
```

### Session Manager (`src.triz_tools.session_manager`)

#### `class SessionManager`

Manages workflow session state and persistence.

**Methods:**

##### `create_session() -> str`

Create new session and return ID.

##### `get_session_data(session_id: str) -> Optional[Dict]`

Retrieve session data.

##### `save_problem_statement(session_id: str, problem: str) -> bool`

Save problem statement.

##### `save_ideal_final_result(session_id: str, ifr: str) -> bool`

Save ideal final result.

##### `save_contradictions(session_id: str, contradictions: List[Dict]) -> bool`

Save identified contradictions.

##### `save_selected_principles(session_id: str, principles: List[int]) -> bool`

Save selected principles.

##### `save_solution_concepts(session_id: str, solutions: List[Dict]) -> bool`

Save generated solutions.

##### `advance_stage(session_id: str) -> str`

Advance to next workflow stage.

##### `reset_session(session_id: str) -> bool`

Reset session to initial state.

##### `export_session(session_id: str, file_path: Path) -> Optional[Dict]`

Export session data.

##### `import_session(file_path: Path) -> Optional[str]`

Import session data.

### Embedding Service (`src.triz_tools.embeddings`)

#### `class EmbeddingClient`

Text embedding generation using Ollama.

**Methods:**

##### `generate(text: str) -> np.ndarray`

Generate embedding for single text.

##### `batch_generate(texts: List[str]) -> List[np.ndarray]`

Generate embeddings for multiple texts.

##### `get_similarity(text1: str, text2: str) -> float`

Calculate cosine similarity between texts.

**Usage:**
```python
from src.triz_tools.embeddings import get_embedding_client

client = get_embedding_client()
embedding = client.generate("reduce weight maintain strength")
```

### Analysis Service (`src.triz_tools.services.analysis_service`)

#### `class AnalysisService`

Core TRIZ analysis functionality.

**Methods:**

##### `identify_contradictions(problem: str) -> List[Dict]`

Identify technical contradictions in problem.

##### `recommend_principles(contradictions: List[Dict]) -> List[int]`

Recommend TRIZ principles for contradictions.

##### `generate_solutions(principles: List[int], context: str) -> List[Dict]`

Generate solution concepts using principles.

##### `evaluate_solutions(solutions: List[Dict], criteria: Dict) -> List[Dict]`

Evaluate and rank solutions.

### Materials Service (`src.triz_tools.services.materials_service`)

#### `class MaterialsService`

Materials database and recommendation service.

**Methods:**

##### `search_materials(query: str, limit: int = 10) -> List[Dict]`

Search materials by properties or applications.

##### `recommend_materials(requirements: str) -> List[Dict]`

Recommend materials based on requirements.

##### `get_material_properties(material_name: str) -> Optional[Dict]`

Get detailed material properties.

## Data Models

### TRIZPrinciple

```python
@dataclass
class TRIZPrinciple:
    id: int
    name: str
    description: str
    examples: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    related_principles: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TRIZPrinciple': ...
```

### EngineeringParameter

```python
@dataclass
class EngineeringParameter:
    id: int
    name: str
    description: str
    examples: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngineeringParameter': ...
```

### MatrixEntry

```python
@dataclass
class MatrixEntry:
    improving_parameter: int
    worsening_parameter: int
    recommended_principles: List[int]
    
    def to_dict(self) -> Dict[str, Any]: ...
```

### SearchResult

```python
@dataclass
class SearchResult:
    principle: TRIZPrinciple
    relevance_score: float
    matched_fields: List[str] = field(default_factory=list)
```

### SessionData

```python
@dataclass
class SessionData:
    session_id: str
    stage: SessionStage
    created_at: datetime
    updated_at: datetime
    problem_statement: Optional[str] = None
    ideal_final_result: Optional[str] = None
    contradictions: List[Dict] = field(default_factory=list)
    selected_principles: List[int] = field(default_factory=list)
    solution_concepts: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### SessionStage (Enum)

```python
class SessionStage(Enum):
    PROBLEM_DEFINITION = "problem_definition"
    IDEAL_FINAL_RESULT = "ideal_final_result"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    PRINCIPLE_SELECTION = "principle_selection"
    SOLUTION_GENERATION = "solution_generation"
    EVALUATION = "evaluation"
```

## Utilities

### Validation (`src.triz_tools.validation`)

#### `@validate_inputs(validators: Dict[str, Callable])`

Decorator for input validation.

#### `class InputValidator`

Static validation methods.

**Methods:**
- `validate_principle_id(principle_id: Any) -> ValidationResult`
- `validate_parameter_id(parameter_id: Any) -> ValidationResult`
- `validate_session_id(session_id: Any) -> ValidationResult`
- `validate_text_input(text: Any, min_length: int = 1) -> ValidationResult`

### Response Formatting (`src.triz_tools.response_formatter`)

#### `class ResponseFormatter`

Standardized response formatting.

**Methods:**
- `format_success(message: str, data: Optional[Dict] = None) -> FormattedResponse`
- `format_error(message: str, error: Optional[str] = None) -> FormattedResponse`
- `format_validation_error(validation_result: ValidationResult) -> FormattedResponse`

### Health Checks (`src.triz_tools.health_checks`)

#### `class HealthChecker`

System health monitoring.

**Methods:**
- `check_all(verbose: bool = False) -> Dict[str, HealthStatus]`
- `check_ollama() -> HealthStatus`
- `check_qdrant() -> HealthStatus`
- `check_knowledge_base() -> HealthStatus`
- `check_sessions() -> HealthStatus`

## Configuration

### Environment Variables

```bash
# Vector Database
TRIZ_QDRANT_HOST=localhost
TRIZ_QDRANT_PORT=6333
TRIZ_QDRANT_COLLECTION_NAME=triz_knowledge

# Embeddings
TRIZ_OLLAMA_HOST=localhost:11434
TRIZ_EMBEDDING_MODEL=nomic-embed-text
TRIZ_EMBEDDING_DIMENSION=768

# Storage
TRIZ_DATA_DIR=./data
TRIZ_CACHE_DIR=./cache
TRIZ_SESSION_DIR=./sessions

# Logging
TRIZ_LOG_LEVEL=INFO
TRIZ_LOG_FORMAT=structured
TRIZ_LOG_FILE=./logs/triz.log

# Performance
TRIZ_CACHE_ENABLED=true
TRIZ_CACHE_SIZE=1000
TRIZ_CACHE_TTL_HOURS=24
```

### Configuration Classes

```python
from src.triz_tools.config import get_config

config = get_config()
print(config.database.qdrant_host)
print(config.embedding.model_name)
```

## Error Handling

### Exception Classes

#### `TRIZError`

Base exception for TRIZ-related errors.

#### `ValidationError`

Input validation errors.

#### `KnowledgeBaseError`

Knowledge base operation errors.

#### `SessionError`

Session management errors.

#### `EmbeddingError`

Embedding generation errors.

### Error Response Format

```python
{
    "success": false,
    "error": "ErrorType",
    "message": "Human-readable error message",
    "details": {
        "field": "validation_error_details",
        "code": "error_code"
    },
    "timestamp": "2024-12-11T10:30:00Z"
}
```

### Error Handling Examples

```python
from src.triz_tools.direct_tools import triz_tool_get_principle
from src.triz_tools.validation import ValidationError

try:
    result = triz_tool_get_principle(999)  # Invalid principle
    if not result["success"]:
        print(f"Error: {result['message']}")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## MCP Server API

### Server Configuration

```python
from src.mcp_server import create_mcp_server

server = create_mcp_server(port=3000, debug=True)
server.run()
```

### Available Tools

#### Request Format

```json
{
    "method": "tools/call",
    "params": {
        "name": "triz_tool_get_principle",
        "arguments": {
            "principle_number": 1
        }
    }
}
```

#### Response Format

```json
{
    "content": [
        {
            "type": "text",
            "text": "Principle 1: Segmentation..."
        }
    ]
}
```

### Tool Definitions

All tools follow the MCP specification with JSON Schema validation for parameters.

## Performance Considerations

### Caching Strategy

- **Embeddings**: Cached for 24 hours by default
- **Knowledge Base**: Loaded once at startup
- **Session Data**: Persisted to disk immediately
- **Matrix Lookups**: In-memory cache

### Memory Usage

- **Knowledge Base**: ~50MB for 40 principles
- **Contradiction Matrix**: ~5MB for 39x39 matrix
- **Session Data**: ~1KB per session
- **Embeddings Cache**: ~1MB per 1000 cached embeddings

### Response Times

- **Tool queries**: < 2 seconds (target)
- **Autonomous solve**: < 10 seconds (target)
- **Workflow steps**: < 1 second (target)
- **Matrix lookups**: < 100ms (target)

## Rate Limiting

Default limits:
- 100 requests per minute per client
- 1000 requests per hour per client
- 10 concurrent autonomous solve operations

## API Versioning

Current API version: `v1`

Version information included in responses:
```python
{
    "api_version": "v1",
    "system_version": "1.0.0",
    "data": {...}
}
```

This API reference provides comprehensive documentation for integrating with the TRIZ Engineering Co-Pilot system.