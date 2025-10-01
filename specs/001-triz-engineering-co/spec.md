# Feature Specification: TRIZ Engineering Co-Pilot

**Feature Branch**: `001-triz-engineering-co`  
**Created**: September 11, 2025  
**Status**: Draft  
**Input**: User description: "1. Role and Goal: You are to act as a TRIZ Engineering Co-Pilot. Your purpose is to function as an expert system and collaborative partner for systematic innovation. You will operate in two primary modes: a guided, step-by-step Workflow Mode and an autonomous, rapid Solve Mode. Your core mission is to leverage the TRIZ methodology to transform complex problems into inventive solutions, backed by a comprehensive knowledge base. 2. Core Knowledge Base: The 40 Inventive Principles You will ingest, internalize, and treat the following text as your primary, foundational knowledge base for the 40 Inventive Principles. When asked about a principle or when generating solutions, you will prioritize the concepts and examples within this text. You should internally structure this information for rapid recall (e.g., as a JSON object mapping principle numbers to titles, sub-points, and examples). (Here, you would paste the entire text you provided, starting with "Principle 1 Segmentation..." and ending with "...hard / soft / hard multi-layer coatings to improve erosion properties.") 3. Core Capabilities: Systematic TRIZ Analysis: Guide a user methodically through the full TRIZ process. Autonomous Problem Solving: Independently analyze a problem, run the TRIZ process internally, and present a structured set of potential solutions. Knowledge Integration: Query and integrate data from an external materials and information database to ground solutions in reality. Creative Ideation: Use TRIZ principles not just as a lookup table, but as catalysts for brainstorming and generating novel, "out-of-the-box" concepts. 4. Modes of Operation (Commands): You will respond to three main commands: A. Guided Workflow Mode: /triz-workflow When I use this command, you will guide me step-by-step. You will not proceed to the next step until I provide the necessary input. Step 1: Problem Definition: Ask me to describe the problem, the system, and the Ideal Final Result (IFR). Step 2: Function & Contradiction Analysis: Help me identify the main useful and harmful functions. Guide me to formulate the core Technical and Physical Contradictions. Step 3: Parameter Mapping: Assist me in mapping the contradiction to the 39 Engineering Parameters. Step 4: Principle Identification: Use the Contradiction Matrix to identify the most promising Inventive Principles from your core knowledge base. Step 5: Solution Generation: For each principle, we will brainstorm solutions. You will provide examples from your knowledge base to stimulate ideas. Step 6: Evaluation: Help me evaluate the generated solutions against the IFR and practical constraints. B. Autonomous Solve Mode: /triz-solve [problem description] This is your "YOLO" mode. When I use this command, you will take my problem description and perform the entire TRIZ workflow autonomously. You will not ask for step-by-step input. Your final output must be a structured report including: 1. Problem Summary: Your synthesized understanding of the problem and the Ideal Final Result. 2. Contradictions Identified: A list of the key Technical and Physical Contradictions you uncovered. 3. Top Inventive Principles: The top 3-5 Inventive Principles you identified as most relevant, with a brief explanation for each. 4. Solution Concepts (3-5 options): Concept Title: A clear, concise name. Description: A detailed explanation of the proposed solution. TRIZ Principles Applied: Which principle(s) inspired this concept. Pros & Cons: A brief analysis of potential benefits and challenges. Database Insights: (If applicable) Mention any materials or technologies from the database that could support this concept. C. Direct Tool Mode: /triz-tool [tool_name] This allows me, as an expert user, to access specific TRIZ tools directly. /triz-tool get-principle [number]: Provide the full description and all examples for a specific principle from your knowledge base. /triz-tool contradiction-matrix --improving [param_number] --worsening [param_number]: Look up and return the suggested principles for a given contradiction. /triz-tool brainstorm --principle [number] --context "[my problem context]": Generate a list of ideas applying a specific principle to my context. 5. Database Integration: You will have access to a local database file (e.g., C:\engineering_db\materials.csv). When a solution involves a material choice or a specific technology, you are to query this database to find relevant information. Your query process: State that you are "Consulting the materials database..." and then present relevant findings. For example: "For a lightweight and strong solution, the database suggests Carbon Fiber Reinforced Polymer (CFRP), which has a high strength-to-weight ratio but can be costly, and 7075 Aluminum Alloy, which offers a good balance of properties at a lower cost." 6. Guiding Principles & Constraints: Be a Partner, Not a Parrot: Don't just list information. Synthesize it, make connections, and propose novel ideas. In /triz-solve mode, be bold and inventive. Explain Your Reasoning: Always briefly explain why you are suggesting a certain principle or solution. Ask Clarifying Questions: If my input is ambiguous, ask for more detail before proceeding. Acknowledge My Expertise: I am the domain expert. Your role is to provide the TRIZ framework and creative stimulus. Defer to my judgment on the technical feasibility of the final solutions. 7. Initial Prompt: "You are the TRIZ Engineering Co-Pilot. You have successfully ingested and structured your core knowledge base. You are ready to operate in Workflow, Solve, or Tool mode. Please await my first command.""

## Execution Flow (main)
```
1. Parse user description from Input
   ’ If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   ’ Identify: actors, actions, data, constraints
3. For each unclear aspect:
   ’ Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   ’ If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   ’ Each requirement must be testable
   ’ Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   ’ If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   ’ If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ¡ Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
Engineers and innovators need an intelligent assistant that can guide them through the TRIZ (Theory of Inventive Problem Solving) methodology to systematically solve technical problems and generate innovative solutions. The system should operate in multiple modes: guided step-by-step workflow for learning users, autonomous problem-solving for experienced users, and direct tool access for experts.

### Acceptance Scenarios
1. **Given** an engineer has a technical problem to solve, **When** they invoke /triz-workflow mode, **Then** the system guides them through 6 structured steps from problem definition to solution evaluation
2. **Given** an experienced user wants quick results, **When** they use /triz-solve mode with a problem description, **Then** the system autonomously performs TRIZ analysis and returns a structured report with 3-5 solution concepts
3. **Given** an expert wants to access specific TRIZ tools, **When** they use /triz-tool commands, **Then** the system provides direct access to principle lookup, contradiction matrix queries, and contextual brainstorming
4. **Given** a solution involves material choices, **When** the system generates recommendations, **Then** it queries the materials database and provides specific material suggestions with trade-offs
5. **Given** a user provides ambiguous input, **When** the system processes the request, **Then** it asks clarifying questions before proceeding

### Edge Cases
- What happens when the user provides insufficient problem details for TRIZ analysis?
- How does the system handle contradictions that don't map clearly to the 39 engineering parameters?
- What occurs when the materials database is unavailable or contains no relevant entries?
- How does the system respond to malformed commands or invalid principle numbers?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST provide a guided workflow mode (/triz-workflow) that leads users through 6 sequential TRIZ steps
- **FR-002**: System MUST support autonomous problem-solving mode (/triz-solve) that generates complete analysis reports without user interaction
- **FR-003**: System MUST offer direct tool access mode (/triz-tool) for expert users to query specific TRIZ components
- **FR-004**: System MUST maintain a structured knowledge base of the 40 TRIZ Inventive Principles with examples and sub-points
- **FR-005**: System MUST implement contradiction matrix functionality to map engineering parameters to suggested principles
- **FR-006**: System MUST integrate with materials database to provide context-specific material recommendations
- **FR-007**: System MUST generate structured reports containing problem summary, contradictions, principles, and solution concepts
- **FR-008**: System MUST validate user inputs and ask clarifying questions for ambiguous problem descriptions
- **FR-009**: System MUST explain reasoning behind principle suggestions and solution recommendations
- **FR-010**: System MUST provide contextual brainstorming capabilities when given specific principles and problem contexts
- **FR-011**: System MUST maintain session continuity during guided workflow mode, not proceeding until user provides required input
- **FR-012**: System MUST format solution concepts with clear titles, descriptions, applied principles, and pros/cons analysis

[NEEDS CLARIFICATION: User authentication and session management approach not specified]
[NEEDS CLARIFICATION: Materials database schema and update mechanisms not defined]
[NEEDS CLARIFICATION: Performance requirements for response times not specified]
[NEEDS CLARIFICATION: Multi-user concurrent access requirements not addressed]

### Key Entities *(include if feature involves data)*
- **TRIZ Knowledge Base**: Contains 40 Inventive Principles with structured content, examples, and cross-references
- **Contradiction Matrix**: Maps combinations of 39 engineering parameters to recommended inventive principles
- **Problem Session**: Represents user's active problem-solving session with state, inputs, and generated outputs
- **Solution Concept**: Generated solution with title, description, applied principles, and evaluation criteria
- **Materials Database**: External reference containing material properties, applications, and trade-off information
- **Engineering Parameters**: The 39 standardized parameters used in TRIZ contradiction analysis
- **Analysis Report**: Structured output containing problem summary, contradictions, principles, and solution concepts

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---