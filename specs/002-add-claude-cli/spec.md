# Feature Specification: Claude CLI Integration for TRIZ Co-Pilot

**Feature Branch**: `002-add-claude-cli`  
**Created**: 2025-01-11  
**Status**: Draft

## 📋 Summary

Enable the TRIZ Engineering Co-Pilot to work seamlessly with Claude CLI (claude.ai/code) in addition to the existing Gemini CLI integration, allowing users to access systematic innovation capabilities through either AI assistant platform.

## 🎯 Problem Statement

Currently, the TRIZ Co-Pilot only supports Google Gemini CLI through MCP server integration. Users who prefer or have access to Claude CLI cannot use the TRIZ systematic innovation tools, limiting the reach and utility of the system. Organizations may have different AI tool preferences or licenses, and supporting multiple platforms increases adoption potential.

## 👥 User Scenarios & Testing

### Scenario 1: Claude CLI User Accesses TRIZ Workflow
**Given**: A user has Claude CLI installed and configured  
**When**: They invoke `/triz-workflow` command in Claude  
**Then**: The guided TRIZ workflow starts, maintaining session state across interactions

### Scenario 2: Seamless Tool Switching
**Given**: A user has both Claude CLI and Gemini CLI available  
**When**: They start a TRIZ session in Claude and later continue in Gemini  
**Then**: The session state persists and the workflow continues from the last step

### Scenario 3: Direct Tool Access in Claude
**Given**: An experienced TRIZ user working in Claude CLI  
**When**: They use `/triz-tool get-principle 15` command  
**Then**: They receive the full Principle 15 (Dynamics) description with examples

### Scenario 4: Autonomous Problem Solving
**Given**: A user describes an engineering problem in Claude CLI  
**When**: They invoke `/triz-solve "reduce weight while maintaining strength"`  
**Then**: Claude analyzes the problem and provides a structured TRIZ solution report

### Scenario 5: Command Discovery
**Given**: A new user opens Claude CLI with TRIZ Co-Pilot  
**When**: They type `/triz` or look for available commands  
**Then**: They see all three TRIZ command options with clear descriptions

## ✅ Functional Requirements

### Tool Registration & Discovery
- [ ] Claude CLI must recognize `/triz-workflow`, `/triz-solve`, and `/triz-tool` commands
- [ ] Commands must appear in Claude's command palette or help system
- [ ] Each command must have clear descriptions of its purpose and usage
- [ ] Command syntax must be identical to Gemini CLI implementation for consistency

### Workflow Mode Integration
- [ ] `/triz-workflow` must guide users through all 6 TRIZ steps sequentially
- [ ] System must wait for user input at each step before proceeding
- [ ] Session state must persist between Claude CLI invocations
- [ ] Progress indicators must show current step (e.g., "Step 3 of 6: Parameter Mapping")

### Autonomous Solve Mode
- [ ] `/triz-solve [problem]` must accept problem descriptions up to 2000 characters
- [ ] System must perform complete TRIZ analysis without step-by-step interaction
- [ ] Output must include: Problem Summary, Contradictions, Top Principles, and 3-5 Solution Concepts
- [ ] Response time must be under 10 seconds for complete analysis

### Direct Tool Mode
- [ ] `/triz-tool get-principle [1-40]` must return principle details from knowledge base
- [ ] `/triz-tool contradiction-matrix --improving [1-39] --worsening [1-39]` must return relevant principles
- [ ] `/triz-tool brainstorm --principle [1-40] --context "[problem]"` must generate contextual ideas
- [ ] Invalid parameters must return helpful error messages with valid ranges

### Session Management
- [ ] Sessions started in Claude must have unique identifiers
- [ ] Session data must be stored in the same format as Gemini sessions
- [ ] Users must be able to resume interrupted sessions with session ID
- [ ] Session timeout must be configurable (default: 24 hours)

### Knowledge Base Access
- [ ] Claude must access the same TRIZ principles database (40 principles)
- [ ] Contradiction matrix (39x39) must be available for lookups
- [ ] Materials database must be searchable when applicable
- [ ] All examples and sub-principles must be retrievable

### Response Formatting
- [ ] Responses must use consistent markdown formatting
- [ ] Numbered lists for principles and solutions
- [ ] Bold headers for sections
- [ ] Code blocks for technical examples when relevant
- [ ] Tables for contradiction matrix results

### Error Handling
- [ ] Missing dependencies must be detected and reported clearly
- [ ] Database connection failures must have fallback to file-based data
- [ ] Invalid commands must suggest closest valid command
- [ ] Network timeouts must not crash the session

### Platform Compatibility
- [ ] Must coexist with Gemini CLI integration without conflicts
- [ ] Shared session storage must be accessible from both platforms
- [ ] Configuration must allow enabling/disabling each integration independently
- [ ] Must support Claude CLI on macOS, Windows, and Linux

## 🔄 Key Entities

### Session
- `session_id`: Unique identifier (UUID)
- `platform`: "claude" | "gemini"  
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `current_stage`: Workflow stage identifier
- `context`: Problem description and analysis data
- `history`: Array of interactions

### Command
- `name`: Command identifier
- `description`: Help text
- `parameters`: Array of parameter definitions
- `examples`: Usage examples
- `handler`: Function reference

### TRIZResponse
- `success`: Boolean
- `message`: User-facing message
- `data`: Response payload
- `session_id`: Associated session
- `stage`: Current workflow stage
- `suggestions`: Next action hints

## ⚠️ Non-Functional Requirements

### Performance
- Command recognition: < 100ms
- Principle lookup: < 500ms  
- Full analysis: < 10 seconds
- Session load/save: < 200ms

### Reliability
- 99.9% uptime for local operations
- Graceful degradation when vector DB unavailable
- Automatic session recovery after crashes
- Data consistency across platforms

### Usability
- Commands discoverable without documentation
- Consistent command syntax across platforms
- Clear error messages with resolution steps
- Progressive disclosure of advanced features

## 🎯 Success Criteria

### Launch Metrics
- [ ] All three TRIZ commands functional in Claude CLI
- [ ] 100% feature parity with Gemini CLI implementation
- [ ] Zero regression in existing Gemini functionality
- [ ] Documentation updated for both platforms

### Quality Metrics
- [ ] All 40 TRIZ principles accessible
- [ ] Session persistence working across platforms
- [ ] Response time within specified limits
- [ ] Error rate < 1% for valid commands

### User Validation
- [ ] New users can discover and use commands without documentation
- [ ] Existing Gemini users can switch to Claude without relearning
- [ ] Power users can leverage both platforms interchangeably
- [ ] [NEEDS CLARIFICATION: User acceptance testing scope and participants?]

## 📐 Constraints & Assumptions

### Technical Constraints
- Must use existing TRIZ knowledge base without modifications
- Must maintain backward compatibility with Gemini CLI
- Cannot modify core TRIZ library logic
- Must work with Claude CLI's current tool registration system

### Assumptions
- Claude CLI supports custom tool registration
- Users have either Claude CLI or Gemini CLI installed (not necessarily both)
- Existing session storage format is platform-agnostic
- Python environment is already configured

### Out of Scope
- Migration of existing Gemini sessions to Claude format
- Real-time synchronization between platforms
- GUI or web interface
- TRIZ knowledge base updates or additions

## 📝 Review & Acceptance Checklist

- [x] Feature can be tested in isolation
- [x] Requirements are specific and measurable  
- [x] User value is clearly articulated
- [x] Success criteria are objective
- [ ] Stakeholder approval obtained [NEEDS CLARIFICATION: Who are stakeholders?]
- [x] No implementation details included
- [x] All user types considered
- [ ] Accessibility requirements defined [NEEDS CLARIFICATION: Any specific accessibility needs?]
- [ ] Security requirements assessed [NEEDS CLARIFICATION: Any data privacy concerns?]
- [x] Performance targets specified

## 🔄 Execution Flow (main)
```
1. Detect Claude CLI environment
   → If not present: WARN "Claude CLI not detected, skipping integration"
2. Register TRIZ commands with Claude
   → For each command: Register handler, description, parameters
3. Initialize shared resources
   → Load knowledge base
   → Connect to session storage
   → Set up vector DB connection (optional)
4. Handle command invocation
   → Parse command and parameters
   → Load/create session
   → Execute appropriate handler
   → Format response for Claude
   → Save session state
5. Return formatted response
   → SUCCESS with TRIZ analysis/data
   → ERROR with helpful message if failed
```

---

## 📋 Quick Guidelines
- Focus on WHAT users need to accomplish with Claude CLI
- Maintain consistency with existing Gemini CLI behavior
- Preserve the three-mode interaction model (Workflow/Solve/Tool)
- Ensure platform-agnostic session management