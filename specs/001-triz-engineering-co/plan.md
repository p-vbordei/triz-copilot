# Implementation Plan: TRIZ Engineering Co-Pilot

**Branch**: `001-triz-engineering-co` | **Date**: September 11, 2025 | **Spec**: [/specs/001-triz-engineering-co/spec.md](/Users/vladbordei/Documents/Development/specs/001-triz-engineering-co/spec.md)
**Input**: Feature specification from `/specs/001-triz-engineering-co/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, GEMINI.md for Gemini CLI
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Primary requirement: Create an intelligent TRIZ (Theory of Inventive Problem Solving) Co-Pilot that extends Google Gemini CLI with systematic innovation capabilities. The system provides three interaction modes: guided workflow for learning users (/triz-workflow), autonomous problem-solving for experienced users (/triz-solve), and direct tool access for experts (/triz-tool). Technical approach leverages local vector database (Qdrant) with Ollama embeddings, session state management, and CLI-only interface to maintain context across multi-step TRIZ processes.

## Technical Context
**Language/Version**: Python 3.11+ (Gemini CLI is Python-based)  
**Primary Dependencies**: google-generativeai, qdrant-client, sentence-transformers, ollama-python, click, pandas  
**Storage**: Local Qdrant vector database + JSON session files  
**Testing**: pytest with real Qdrant container  
**Target Platform**: macOS M4 with local Ollama embeddings
**Project Type**: single (CLI tool extension)  
**Performance Goals**: <2s response time for tool queries, <10s for autonomous solve mode  
**Constraints**: Local-first (no cloud dependencies), minimal changes to base Gemini CLI, CLI-only interface  
**Scale/Scope**: Single user, 40 TRIZ principles, thousands of solution examples, materials database with ~1000 entries

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 3 (triz-tools library, cli extension, tests)
- Using framework directly? Yes (Gemini CLI tool discovery, Qdrant client)
- Single data model? Yes (TRIZ knowledge base with vector embeddings)
- Avoiding patterns? Yes (direct function calls, no unnecessary abstractions)

**Architecture**:
- EVERY feature as library? Yes (triz-tools as standalone library)
- Libraries listed: triz-tools (TRIZ logic, vector queries, session management)
- CLI per library: Integrated via Gemini CLI tool discovery mechanism
- Library docs: llms.txt format planned for GEMINI.md

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (tests fail before implementation)
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual Qdrant container, not mocks)
- Integration tests for: tool integration with Gemini CLI, vector search accuracy, session continuity
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (Python logging with structured format)
- Frontend logs → backend? N/A (CLI only)
- Error context sufficient? Yes (detailed error messages with context)

**Versioning**:
- Version number assigned? 1.0.0 (new feature)
- BUILD increments on every change? Yes
- Breaking changes handled? Yes (version compatibility checks)

## Project Structure

### Documentation (this feature)
```
specs/001-triz-engineering-co/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── triz_tools/          # Core TRIZ library
│   ├── __init__.py
│   ├── knowledge_base.py    # Vector DB operations
│   ├── contradiction_matrix.py  # TRIZ matrix logic
│   ├── session_manager.py   # State management
│   └── embeddings.py        # Ollama integration
├── gemini_extensions/   # Gemini CLI integration
│   └── triz_tool.py     # Tool registration and commands
└── data/
    ├── triz_principles.txt  # 40 principles knowledge
    ├── contradiction_matrix.json
    └── materials_database.csv

tests/
├── contract/            # Tool interface contracts
├── integration/         # Gemini CLI integration tests
└── unit/               # Individual function tests
```

**Structure Decision**: Option 1 (single project) - CLI tool extension pattern

## Phase 0: Outline & Research

### Unknowns to Research
1. **Gemini CLI Tool Discovery Mechanism**: How to register custom tools with Gemini CLI
2. **Ollama Integration on macOS M4**: Optimal embedding models and performance
3. **Qdrant Collection Design**: Vector dimensions, distance metrics for TRIZ data
4. **Session State Persistence**: File-based vs. memory-based state management
5. **TRIZ Contradiction Matrix**: Data structure and lookup optimization

### Research Tasks
- Research Gemini CLI architecture and tool registration patterns
- Evaluate Ollama embedding models for technical text (all-MiniLM-L6-v2 vs alternatives)
- Design Qdrant schema for TRIZ principles, materials data, and solution examples
- Analyze TRIZ methodology workflow for state transition modeling
- Investigate CLI command parsing patterns in existing Gemini CLI codebase

**Output**: research.md with all technical decisions resolved

## Phase 1: Design & Contracts

### Data Model Extraction
From feature spec entities:
- **TRIZ Knowledge Base**: 40 principles with structured content, examples, embeddings
- **Contradiction Matrix**: 39x39 parameter mapping to recommended principles
- **Problem Session**: Active session state with workflow stage, user inputs, generated outputs
- **Solution Concept**: Generated solutions with metadata and evaluation criteria
- **Materials Database**: Material properties with vector embeddings for similarity search

### API Contracts
Tool interface contracts for Gemini CLI:
- `/triz-workflow [start|continue|reset]`: Interactive guided workflow
- `/triz-solve <problem_description>`: Autonomous problem-solving
- `/triz-tool get-principle <number>`: Direct principle lookup
- `/triz-tool contradiction-matrix --improving <param> --worsening <param>`: Matrix query
- `/triz-tool brainstorm --principle <number> --context "<context>"`: Contextual ideation

### Contract Tests
- Test tool registration with Gemini CLI
- Validate command parsing and parameter handling
- Assert proper response formatting (JSON + human-readable)
- Verify session state continuity across commands

### Integration Scenarios
- Complete /triz-workflow session from problem to solutions
- Autonomous /triz-solve with complex engineering problem
- Direct /triz-tool access for expert users
- Error handling for invalid inputs and system failures

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, GEMINI.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from TRIZ tool contracts and data model
- Each tool interface → contract test task [P]
- Each TRIZ entity (principles, matrix, sessions) → model creation task [P]
- Each user workflow → integration test task
- Vector database setup and ingestion tasks
- Ollama integration and embedding tasks
- Gemini CLI tool registration tasks

**Ordering Strategy**:
- TDD order: Contract tests → Integration tests → Implementation
- Dependency order: Data models → Vector DB → Tool logic → CLI integration
- Infrastructure first: Qdrant setup → Ollama setup → Knowledge ingestion
- Mark [P] for parallel execution (independent components)

**Estimated Output**: 28-32 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*All complexity appears justified by constitutional principles*

No violations detected. Single project structure with library-first approach maintains simplicity while meeting CLI extension requirements.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*