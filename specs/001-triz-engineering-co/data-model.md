# Data Model: TRIZ Engineering Co-Pilot

## Entity Definitions

### 1. TRIZ Knowledge Base
**Purpose**: Core repository of the 40 TRIZ Inventive Principles with structured content and examples

**Fields**:
- `principle_id` (int): Unique identifier (1-40)
- `principle_name` (string): Official TRIZ principle name
- `principle_number` (int): Standard TRIZ numbering
- `description` (text): Detailed explanation of the principle
- `sub_principles` (array): List of sub-categories or variations
- `examples` (array): Practical applications and case studies
- `patent_references` (array): Related patent numbers
- `domains` (array): Applicable engineering domains
- `contradiction_params` (array): Related engineering parameters (1-39)
- `usage_frequency` (enum): high|medium|low
- `innovation_level` (int): Complexity level 1-5
- `related_principles` (array): Cross-references to other principles

**Relationships**:
- Many-to-many with Engineering Parameters
- One-to-many with Solution Concepts
- Many-to-many with Case Studies

### 2. Contradiction Matrix
**Purpose**: Maps combinations of 39 engineering parameters to recommended inventive principles

**Fields**:
- `improving_parameter` (int): Parameter that needs improvement (1-39)
- `worsening_parameter` (int): Parameter that gets worse (1-39)
- `recommended_principles` (array): List of applicable principle IDs
- `confidence_score` (float): Statistical reliability 0.0-1.0
- `application_frequency` (int): Number of successful applications
- `last_updated` (datetime): Matrix entry update timestamp

**Validation Rules**:
- Both parameters must be in range 1-39
- Cannot have identical improving and worsening parameters
- Recommended principles must exist in Knowledge Base
- Confidence score must be 0.0-1.0

### 3. Problem Session
**Purpose**: Represents user's active problem-solving session with state and progress

**Fields**:
- `session_id` (uuid): Unique session identifier
- `created_at` (datetime): Session creation timestamp
- `last_activity` (datetime): Last user interaction
- `workflow_type` (enum): guided|autonomous|tool
- `current_stage` (enum): problem_definition|contradiction_analysis|principle_selection|solution_generation|evaluation|completed
- `problem_statement` (text): User's problem description
- `system_description` (text): Technical system context
- `ideal_final_result` (text): User's desired outcome
- `session_data` (json): Stage-specific data and progress
- `user_inputs` (json): Historical user responses
- `ai_outputs` (json): Generated recommendations and analysis

**State Transitions**:
- problem_definition → contradiction_analysis
- contradiction_analysis → principle_selection  
- principle_selection → solution_generation
- solution_generation → evaluation
- evaluation → completed (or back to any previous stage)

### 4. Solution Concept
**Purpose**: Generated solution with applied principles and evaluation criteria

**Fields**:
- `solution_id` (uuid): Unique solution identifier
- `session_id` (uuid): Parent session reference
- `concept_title` (string): Clear, concise solution name
- `description` (text): Detailed solution explanation
- `applied_principles` (array): TRIZ principles used
- `principle_applications` (json): How each principle was applied
- `innovation_level` (int): Novelty assessment 1-5
- `feasibility_score` (float): Implementation difficulty 0.0-1.0
- `effectiveness_score` (float): Expected problem resolution 0.0-1.0
- `pros` (array): Solution advantages
- `cons` (array): Solution disadvantages and risks
- `materials_suggested` (array): Recommended materials
- `implementation_steps` (array): High-level implementation guidance
- `patents_to_review` (array): Related intellectual property
- `estimated_cost` (enum): low|medium|high
- `development_time` (enum): short|medium|long

**Validation Rules**:
- Must reference valid session_id
- Applied principles must exist in Knowledge Base
- Scores must be in valid ranges 0.0-1.0
- At least one principle must be applied

### 5. Materials Database
**Purpose**: External reference containing material properties and engineering trade-offs

**Fields**:
- `material_id` (string): Unique material identifier
- `material_name` (string): Common name
- `material_class` (string): Category (metals, polymers, ceramics, composites)
- `chemical_formula` (string): Chemical composition
- `mechanical_properties` (json): Strength, modulus, hardness, etc.
- `thermal_properties` (json): Conductivity, expansion, melting point
- `electrical_properties` (json): Resistivity, permittivity
- `physical_properties` (json): Density, color, texture
- `applications` (array): Typical use cases
- `advantages` (array): Material strengths
- `disadvantages` (array): Material limitations
- `cost_index` (float): Relative cost 1.0-10.0
- `availability` (enum): research|limited|commercial|commodity
- `sustainability_score` (float): Environmental impact 1.0-10.0
- `similar_materials` (array): Alternative material suggestions
- `triz_parameters` (array): Related TRIZ engineering parameters

### 6. Engineering Parameters
**Purpose**: The 39 standardized parameters used in TRIZ contradiction analysis

**Fields**:
- `parameter_id` (int): Standard TRIZ parameter number (1-39)
- `parameter_name` (string): Official TRIZ parameter name
- `description` (text): Detailed parameter explanation
- `measurement_units` (array): Applicable units of measurement
- `typical_domains` (array): Engineering fields where parameter is relevant
- `improvement_methods` (array): General approaches to improve parameter
- `measurement_techniques` (array): How to quantify parameter
- `related_parameters` (array): Parameters often in contradiction
- `common_contradictions` (array): Frequent contradiction pairs

**Static Data**: Fixed set of 39 parameters from TRIZ methodology

### 7. Analysis Report
**Purpose**: Structured output containing problem summary, contradictions, principles, and solution concepts

**Fields**:
- `report_id` (uuid): Unique report identifier
- `session_id` (uuid): Source session reference
- `generated_at` (datetime): Report creation timestamp
- `report_type` (enum): workflow_summary|autonomous_solve|tool_analysis
- `problem_summary` (text): Synthesized problem understanding
- `ideal_final_result` (text): Identified target outcome
- `contradictions_identified` (array): Technical and physical contradictions
- `contradiction_analysis` (json): Detailed contradiction breakdown
- `top_principles` (array): Most relevant TRIZ principles
- `principle_rationale` (json): Why each principle was selected
- `solution_concepts` (array): Generated solution options
- `evaluation_matrix` (json): Solution comparison criteria
- `recommendations` (array): Implementation priorities
- `materials_analysis` (json): Material selection insights
- `next_steps` (array): Suggested follow-up actions
- `confidence_score` (float): Overall analysis confidence 0.0-1.0

**Validation Rules**:
- Must reference valid session_id
- At least one contradiction must be identified
- At least one principle must be selected
- Solution concepts must reference valid principles

## Data Relationships

### Primary Relationships
```
TRIZ Knowledge Base (1) ←→ (M) Solution Concepts
Contradiction Matrix (1) ←→ (M) TRIZ Knowledge Base
Problem Session (1) ←→ (M) Solution Concepts
Problem Session (1) ←→ (1) Analysis Report
Engineering Parameters (M) ←→ (M) TRIZ Knowledge Base
Materials Database (M) ←→ (M) Solution Concepts
```

### Cross-Reference Patterns
- **Principle Discovery**: Parameters → Contradiction Matrix → Principles
- **Solution Generation**: Principles + Materials → Solution Concepts
- **Session Flow**: Problem Session → Solutions → Analysis Report
- **Knowledge Lookup**: Principle ID → Full principle details + examples

## Vector Embedding Schema

### Embedded Entities
All text-heavy entities require vector embeddings for semantic search:

**TRIZ Knowledge Base**:
- `description_vector` (768D): Main principle description
- `examples_vector` (768D): Combined examples text
- `applications_vector` (384D): Application domains text

**Materials Database**:
- `properties_vector` (512D): Numerical properties embedding
- `applications_vector` (768D): Use cases and descriptions
- `trade_offs_vector` (384D): Advantages and disadvantages

**Solution Concepts**:
- `description_vector` (768D): Full solution description
- `outcome_vector` (384D): Expected results and benefits

**Problem Sessions**:
- `problem_vector` (768D): Combined problem statement and context

## Validation Rules Summary

### Data Integrity
- All foreign key references must be valid
- Enum fields must match allowed values
- Numerical scores must be within specified ranges
- Required fields cannot be null or empty

### Business Logic
- Session workflows must follow valid state transitions
- Contradiction matrix entries must be logically consistent
- Solution concepts must apply at least one valid TRIZ principle
- Materials recommendations must match problem constraints

### Performance Constraints
- Vector embeddings must be pre-computed for all searchable entities
- Session data should be indexed by user and timestamp
- Principle lookups must support O(1) access by ID
- Cross-references should use efficient join patterns