# TRIZ Complete Implementation - Product Requirements Document

## PROJECT STATUS: 45% COMPLETE

**Completed:**
- ✅ Complete TRIZ data models (`src/triz_tools/triz_models.py`)
- ✅ Phase 1 instructions: Understand & Scope (Steps 1-10)
- ✅ Phase 2 instructions: Define Ideal (Steps 11-16)
- ✅ Phase 3 instructions: Function Analysis (Steps 17-26)
- ✅ Phase 4 instructions: Select Tools (Steps 27-32)
- ✅ Backup of original solver

**Remaining Work:**
- ❌ Phase 5 instructions: Generate Solutions (Steps 33-50) - **18 STEPS**
- ❌ Phase 6 instructions: Rank & Implement (Steps 51-60) - **10 STEPS**
- ❌ Complete 60-step solver engine (`src/triz_tools/guided_triz_solver.py`)
- ❌ MCP handler for guided research (`src/claude_tools/guided_handler.py`)
- ❌ Update `src/claude_mcp_server.py` with new tools
- ❌ Create 76 Standard Solutions database
- ❌ Create 8 Trends database
- ❌ Testing

---

## CRITICAL REQUIREMENTS

### 1. DO NOT CREATE CONCENTRATED/SIMPLIFIED VERSIONS
- Every step must be FULLY detailed with:
  - 4-5 search queries minimum
  - 4-5 extract_requirements minimum
  - Detailed expected_output_format with example JSON
  - Comprehensive why_this_matters explanation
  - Related TRIZ tool reference

### 2. FOLLOW EXACT PATTERN FROM PHASES 1-4
- Look at `src/triz_tools/guided_steps/phase1_understand_scope.py` as the TEMPLATE
- Each step must be equally detailed
- Each step must build on accumulated_knowledge from previous steps
- Each step must validate findings thoroughly

### 3. ACADEMIC TRIZ METHODOLOGY COMPLIANCE
- Based on official TRIZ documentation in `/CLAUDE.md` and `TRIZ_academic_paper.md`
- Must implement ALL tools: 9 Boxes, Ideality, Function Analysis, 76 Standard Solutions, 40 Principles, 8 Trends, Effects Database
- Must follow the 6-phase process exactly

---

## IMPLEMENTATION TASKS

### TASK 1: Complete Phase 5 Instructions (18 Steps: 33-50)

**File:** `src/triz_tools/guided_steps/phase5_generate_solutions.py`

**Structure:**
```python
"""
PHASE 5: GENERATE SOLUTIONS (Steps 33-50)

Apply ALL selected TRIZ tools to generate comprehensive solution set.
This is the LONGEST phase with 18 steps of deep research.

Steps:
33. Deep research Principle #1 from matrix (full description)
34. Find real-world examples of Principle #1
35. Extract sub-principles and variations of Principle #1
36. Apply Principle #1 to your specific problem
37. Deep research Principle #2 from matrix (full description)
38. Find real-world examples of Principle #2
39. Extract sub-principles and variations of Principle #2
40. Apply Principle #2 to your specific problem
41. Research Principle #3 (if applicable)
42. Apply Standard Solution: Eliminate harm
43. Apply Standard Solution: Block harm (if elimination impossible)
44. Apply Standard Solution: Convert harm to benefit
45. Apply Standard Solution: Enhance insufficient functions
46. Research effects from Effects Database for new functions
47. DEEP materials research (if materials problem detected)
48. Extract material properties: densities, strengths, formability
49. Create material comparison tables
50. Generate complete solution concepts combining all tools
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]) -> StepInstruction:
    """Generate instruction for Phase 5 steps"""
    
    # Get recommended principles from step 29
    principles = accumulated_knowledge.get("step_29", {}).get("recommended_principles", [])
    
    # Get harmful functions from step 21
    harms = accumulated_knowledge.get("step_21", {}).get("harmful_functions", [])
    
    # Get insufficient functions from step 19
    insufficient = accumulated_knowledge.get("step_19", {}).get("insufficient_functions", [])
    
    if step_num == 33:
        # Get first principle number from matrix results
        principle_num = principles[0] if principles else 1
        
        return StepInstruction(
            task=f"Deep research TRIZ Principle #{principle_num} - read FULL description from knowledge base",
            search_queries=[
                f"TRIZ principle {principle_num} full description",
                f"principle {principle_num} definition explanation examples",
                f"how to apply principle {principle_num}",
                f"principle {principle_num} sub-principles variations"
            ],
            extract_requirements=[
                "principle_number",
                "principle_name",
                "full_description",         # Complete description, not summary
                "general_approach",         # How it works conceptually
                "when_to_use"               # Appropriate situations
            ],
            validation_criteria=f"Must extract COMPLETE description of Principle #{principle_num} with at least 200 words",
            expected_output_format=f"""
            {{
                "principle_number": {principle_num},
                "principle_name": "Principle Name Here",
                "full_description": "COMPLETE multi-paragraph description from TRIZ books...",
                "general_approach": "This principle works by...",
                "when_to_use": "Use this when you need to...",
                "source": "TRIZ_book_name"
            }}
            """,
            why_this_matters=f"Understanding the FULL principle #{principle_num} is critical before applying it. Shallow understanding leads to poor solutions.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num}"
        )
    
    elif step_num == 34:
        principle_num = accumulated_knowledge.get("step_33", {}).get("principle_number", 1)
        
        return StepInstruction(
            task=f"Find real-world examples of Principle #{principle_num} in action",
            search_queries=[
                f"principle {principle_num} examples case studies",
                f"principle {principle_num} applications industry",
                f"principle {principle_num} success stories",
                f"how companies used principle {principle_num}"
            ],
            extract_requirements=[
                "examples_list",            # At least 5 examples
                "example_domain",           # Industry/field
                "how_principle_applied",    # Specific application
                "results_achieved",         # What was the outcome?
                "applicability_to_problem"  # Can we adapt this?
            ],
            validation_criteria=f"Must find at least 5 real-world examples of Principle #{principle_num} from research",
            expected_output_format="""
            {
                "examples": [
                    {
                        "example": "Example description",
                        "domain": "aerospace/automotive/medical/etc",
                        "application": "How they applied the principle",
                        "results": "What they achieved",
                        "source": "book_name or journal",
                        "applicability": "HIGH/MEDIUM/LOW - why?"
                    },
                    ... (at least 5 examples)
                ]
            }
            """,
            why_this_matters=f"Real examples show HOW to apply Principle #{principle_num} in practice, not just theory.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Examples"
        )
    
    # CONTINUE FOR STEPS 35-50...
    # Each step must follow this EXACT level of detail
    
    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 5 (valid: 33-50)")
```

**Requirements for Steps 35-50:**

- **Step 35:** Extract sub-principles of Principle #1
- **Step 36:** Apply Principle #1 to YOUR specific problem with concrete solution
- **Step 37:** Deep research Principle #2 (same as step 33)
- **Step 38:** Examples of Principle #2 (same as step 34)
- **Step 39:** Sub-principles of Principle #2 (same as step 35)
- **Step 40:** Apply Principle #2 to problem (same as step 36)
- **Step 41:** Research Principle #3 if recommended (same depth as 33-40)
- **Step 42:** Apply Standard Solution: ELIMINATE harmful function
  - Research harm elimination techniques
  - Find examples of eliminating similar harms
  - Propose concrete elimination methods
- **Step 43:** Apply Standard Solution: BLOCK harmful function
  - Research blocking/shielding techniques
  - Find examples where harm couldn't be eliminated but was blocked
  - Propose blocking methods
- **Step 44:** Apply Standard Solution: CONVERT harm to benefit
  - Research waste-to-value examples
  - Find examples of turning problems into opportunities
  - Propose conversion methods
- **Step 45:** Apply Standard Solution: ENHANCE insufficient functions
  - Research amplification/boosting techniques
  - Find examples of enhancing weak functions
  - Propose enhancement methods
- **Step 46:** Research Effects Database for new functions
  - Search for scientific effects that deliver needed functions
  - Find X-Factor matches (Subject-Action-Object)
  - Propose implementation using effects
- **Step 47:** DEEP materials research (if materials problem)
  - Search 44+ materials engineering books
  - Target specific materials identified in previous steps
  - Extract comprehensive properties
- **Step 48:** Extract material properties with regex
  - Densities (g/cm³)
  - Strengths (MPa)
  - Formability characteristics
  - Manufacturing properties
- **Step 49:** Create material comparison tables
  - Compare 5+ materials side-by-side
  - Calculate weight vs aluminum percentages
  - Rank by Ideality contribution
- **Step 50:** Synthesize ALL findings into complete solution concepts
  - Combine multiple principles
  - Integrate Standard Solutions
  - Include materials recommendations
  - Create 5+ solution concepts

**Each step must:**
1. Use accumulated_knowledge from ALL previous steps
2. Have 4-5 detailed search_queries
3. Have 4-5 specific extract_requirements
4. Have example JSON with realistic data
5. Explain why_this_matters in 2-3 sentences
6. Reference the specific TRIZ tool being used

---

### TASK 2: Complete Phase 6 Instructions (10 Steps: 51-60)

**File:** `src/triz_tools/guided_steps/phase6_rank_implement.py`

**Structure:**
```python
"""
PHASE 6: RANK & IMPLEMENT (Steps 51-60)

Evaluate all solution concepts using Ideality.
Rank solutions on Ideality Plot.
Create implementation plan.

Steps:
51. Calculate Ideality for each solution concept
52. Calculate expected benefits for each solution
53. Calculate expected costs for each solution
54. Calculate expected harms for each solution
55. Create Ideality Plot with all solutions
56. Categorize solutions (Implement Now, Improve, Research, Park)
57. Select top 3 solutions for implementation
58. Research implementation requirements (suppliers, tech, resources)
59. Create detailed implementation timeline
60. Generate final synthesis with complete evidence
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]) -> StepInstruction:
    """Generate instruction for Phase 6 steps"""
    
    # Get solution concepts from step 50
    solutions = accumulated_knowledge.get("step_50", {}).get("solution_concepts", [])
    
    if step_num == 51:
        return StepInstruction(
            task="Calculate Ideality score for EACH solution concept",
            search_queries=[
                "ideality calculation formula TRIZ",
                "evaluate solution concepts benefits costs harms",
                "how to score solutions ideality metric"
            ],
            extract_requirements=[
                "solution_evaluations",     # Ideality for each solution
                "calculation_method",       # How calculated
                "ideality_scores",          # Numerical scores
                "ranking_order"             # Solutions ranked by Ideality
            ],
            validation_criteria=f"Must calculate Ideality for ALL {len(solutions) if solutions else 5} solution concepts from Step 50",
            expected_output_format="""
            {
                "evaluations": [
                    {
                        "solution": "Solution 1 name",
                        "benefits_sum": 45.0,
                        "costs_sum": 15.0,
                        "harms_sum": 5.0,
                        "ideality_score": 2.25,
                        "category": "EXCELLENT"
                    },
                    ... (for each solution)
                ],
                "ranking": ["Solution 1", "Solution 3", "Solution 2", ...]
            }
            """,
            why_this_matters="Ideality score is THE metric for ranking solutions. Highest Ideality = best solution.",
            related_triz_tool="Ideality Equation + Ideality Plot"
        )
    
    # CONTINUE FOR STEPS 52-60...
    # Each step must follow this EXACT level of detail
    
    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 6 (valid: 51-60)")
```

**Requirements for Steps 52-60:**

- **Step 52:** Calculate expected benefits for each solution
  - List all benefits each solution provides
  - Rate importance (1-10)
  - Estimate achievement level (0-10)
  - Research evidence for estimates
- **Step 53:** Calculate expected costs for each solution
  - Money, time, materials, effort, energy
  - Rate magnitude (1-10)
  - Research actual costs from similar implementations
- **Step 54:** Calculate expected harms for each solution
  - Safety, environmental, waste, side-effects
  - Rate severity (1-10)
  - Research potential problems
- **Step 55:** Create Ideality Plot with all solutions
  - Plot on 2D graph: Ideality vs Feasibility
  - Categorize quadrants
  - Identify best solutions visually
- **Step 56:** Categorize solutions into 4 groups
  - **Implement Now:** High Ideality, high feasibility → DO THESE
  - **Further TRIZ:** High benefits but big problems → iterate TRIZ
  - **Improve:** Low benefits → enhance or discard
  - **Park:** Keep for future consideration
- **Step 57:** Select top 3 solutions for detailed implementation
  - Justify selection based on Ideality + feasibility + innovation
  - Compare pros/cons
  - Recommend primary + backup solutions
- **Step 58:** Research implementation requirements
  - Suppliers for materials/components
  - Technologies needed
  - Manufacturing processes
  - Cost estimates
  - Lead times
- **Step 59:** Create detailed implementation timeline
  - Phase 1: Design (weeks 1-2)
  - Phase 2: Prototyping (weeks 3-4)
  - Phase 3: Testing (weeks 5-6)
  - Phase 4: Refinement (weeks 7-8)
  - Phase 5: Production (weeks 9+)
- **Step 60:** Generate final synthesis with ALL evidence
  - Problem statement
  - Complete TRIZ analysis summary
  - Recommended solution with full justification
  - Evidence from all 59 previous steps
  - Implementation roadmap
  - Anticipated future problems (next TRIZ iteration)

---

### TASK 3: Build Complete 60-Step Solver Engine

**File:** `src/triz_tools/guided_triz_solver.py` (rewrite completely)

**Requirements:**

```python
"""
Complete TRIZ Guided Solver - 60 Steps
Official TRIZ Methodology Implementation

This implements the complete 6-phase TRIZ process as 60 guided research steps.
Each step returns research instructions for the AI, NOT solutions.
The AI must perform 60 iterations of research and validation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime

from .triz_models import (
    TRIZGuidedSession,
    TRIZStep,
    TRIZPhase,
    StepStatus,
    StepInstruction,
    NineBoxes,
    Ideality,
    IdealOutcome,
    FunctionMap,
    TechnicalContradiction,
    PhysicalContradiction,
    SolutionConcept,
    Resource
)


class GuidedTRIZSolver:
    """
    Complete TRIZ Guided Solver - 60 steps
    
    This class does NOT solve problems directly.
    It GUIDES the AI through 60 research steps to discover solutions.
    """
    
    def __init__(self):
        self.sessions_dir = Path(__file__).parent.parent / "data" / "guided_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def start_guided_session(self, problem: str) -> Dict[str, Any]:
        """
        Start new guided TRIZ research session.
        
        Returns:
            Dict with session_id and Step 1 instructions
        """
        session_id = str(uuid.uuid4())[:8]
        
        # Initialize all 60 steps
        steps = self._initialize_60_steps()
        
        session = TRIZGuidedSession(
            session_id=session_id,
            problem=problem,
            current_step=1,
            steps=steps,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Generate Step 1 instruction
        from .guided_steps import phase1_understand_scope
        step_1_instruction = phase1_understand_scope.generate(1, problem, {})
        
        session.steps[0].instruction = step_1_instruction
        session.steps[0].status = StepStatus.AWAITING_RESEARCH
        
        self._save_session(session)
        
        return {
            "session_id": session_id,
            "total_steps": 60,
            "current_step": 1,
            "phase": "UNDERSTAND_SCOPE",
            "phase_description": "Create 9 Boxes context map and calculate current Ideality",
            "instruction": self._format_instruction(step_1_instruction),
            "context": {
                "problem": problem,
                "progress": "1/60 steps (2%)",
                "phase_progress": "Step 1 of 10 in Phase 1"
            }
        }
    
    def submit_research(
        self,
        session_id: str,
        findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit research findings for current step.
        
        Args:
            session_id: Session ID
            findings: Research findings (must match extract_requirements)
            
        Returns:
            Validation result and next step instructions (or final solution if step 60)
        """
        session = self._load_session(session_id)
        
        if not session:
            return {
                "success": False,
                "error": f"Session {session_id} not found"
            }
        
        current_step_num = session.current_step
        current_step = session.steps[current_step_num - 1]
        
        # Validate findings
        validation = self._validate_findings(current_step, findings)
        
        if not validation["valid"]:
            return {
                "success": False,
                "validation_failed": True,
                "current_step": current_step_num,
                "error": validation["error"],
                "hint": validation.get("hint", ""),
                "instruction": self._format_instruction(current_step.instruction),
                "progress": f"{current_step_num}/60 steps ({int(current_step_num/60*100)}%)"
            }
        
        # Store validated findings
        current_step.findings = findings
        current_step.status = StepStatus.VALIDATED
        current_step.validation_result = validation["message"]
        
        # Update accumulated knowledge
        self._update_accumulated_knowledge(session, current_step_num, findings)
        
        # Update TRIZ artifacts
        self._update_triz_artifacts(session, current_step_num, findings)
        
        # Check if final step
        if current_step_num >= 60:
            final_solution = self._generate_final_solution(session)
            self._save_session(session)
            
            return {
                "success": True,
                "completed": True,
                "total_steps": 60,
                "final_solution": final_solution,
                "session_summary": self._generate_session_summary(session),
                "triz_artifacts": {
                    "nine_boxes": session.nine_boxes,
                    "current_ideality": session.current_ideality,
                    "ideal_outcome": session.ideal_outcome,
                    "function_map": session.function_map,
                    "contradictions": {
                        "technical": session.technical_contradictions,
                        "physical": session.physical_contradictions
                    },
                    "solutions": session.solution_concepts
                }
            }
        
        # Move to next step
        next_step_num = current_step_num + 1
        session.current_step = next_step_num
        
        # Generate next step instruction
        next_instruction = self._generate_step_instruction(
            next_step_num,
            session.problem,
            session.accumulated_knowledge
        )
        
        next_step = session.steps[next_step_num - 1]
        next_step.instruction = next_instruction
        next_step.status = StepStatus.AWAITING_RESEARCH
        
        session.updated_at = datetime.now().isoformat()
        self._save_session(session)
        
        return {
            "success": True,
            "validation": validation["message"],
            "step_completed": current_step_num,
            "current_step": next_step_num,
            "total_steps": 60,
            "phase": session.current_phase.value,
            "phase_description": self._get_phase_description(session.current_phase),
            "instruction": self._format_instruction(next_instruction),
            "context": session.accumulated_knowledge,
            "progress": f"{next_step_num}/60 steps ({int(next_step_num/60*100)}%)",
            "phase_progress": self._get_phase_progress(next_step_num)
        }
    
    def _initialize_60_steps(self) -> List[TRIZStep]:
        """Initialize all 60 steps with metadata"""
        steps = []
        
        # PHASE 1: Understand & Scope (Steps 1-10)
        phase1_titles = [
            "Create 9 Boxes context map",
            "Research Sub-System components",
            "Research Super-System environment",
            "Analyze Past evolution",
            "Analyze Future trends",
            "Identify all current Benefits",
            "Identify all current Costs",
            "Identify all current Harms",
            "Calculate current Ideality score",
            "Identify root causes from 9 Boxes"
        ]
        for i, title in enumerate(phase1_titles, 1):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.UNDERSTAND_SCOPE,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="9 Boxes + Ideality Audit"
            ))
        
        # PHASE 2: Define Ideal (Steps 11-16)
        phase2_titles = [
            "Create Ideal Outcome wish list",
            "Research ideal systems in other domains",
            "Identify Resources (Substance, Field, Space, Time, Information)",
            "Research resource utilization examples",
            "Define Ideal System in 9 Boxes",
            "Calculate Ideal Ideality target"
        ]
        for i, title in enumerate(phase2_titles, 11):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.DEFINE_IDEAL,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="Ideal Outcome + Resources"
            ))
        
        # PHASE 3: Function Analysis (Steps 17-26)
        phase3_titles = [
            "Map all Subject-Action-Object relationships",
            "Categorize: Useful functions",
            "Categorize: Insufficient functions",
            "Categorize: Excessive functions",
            "Categorize: Harmful functions",
            "Research harm elimination examples",
            "Identify Technical Contradictions",
            "Identify Physical Contradictions",
            "Research contradiction resolution examples",
            "Prioritize problems to solve"
        ]
        for i, title in enumerate(phase3_titles, 17):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.FUNCTION_ANALYSIS,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="Function Analysis + Contradictions"
            ))
        
        # PHASE 4: Select Tools (Steps 27-32)
        phase4_titles = [
            "Match problems to TRIZ tool categories",
            "Map contradictions to 39 Parameters",
            "Lookup Contradiction Matrix",
            "Identify Standard Solutions for harms",
            "Search Effects Database for functions",
            "Research Evolution Trends"
        ]
        for i, title in enumerate(phase4_titles, 27):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.SELECT_TOOLS,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="Tool Selection Logic"
            ))
        
        # PHASE 5: Generate Solutions (Steps 33-50) - 18 STEPS
        phase5_titles = [
            "Deep research Principle #1",
            "Find examples of Principle #1",
            "Extract sub-principles of Principle #1",
            "Apply Principle #1 to problem",
            "Deep research Principle #2",
            "Find examples of Principle #2",
            "Extract sub-principles of Principle #2",
            "Apply Principle #2 to problem",
            "Research Principle #3 if applicable",
            "Apply Standard Solution: Eliminate harm",
            "Apply Standard Solution: Block harm",
            "Apply Standard Solution: Convert harm to benefit",
            "Apply Standard Solution: Enhance insufficient functions",
            "Research Effects Database for new functions",
            "DEEP materials research",
            "Extract material properties (density, strength, formability)",
            "Create material comparison tables",
            "Synthesize complete solution concepts"
        ]
        for i, title in enumerate(phase5_titles, 33):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.GENERATE_SOLUTIONS,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="40 Principles + Standard Solutions + Effects"
            ))
        
        # PHASE 6: Rank & Implement (Steps 51-60) - 10 STEPS
        phase6_titles = [
            "Calculate Ideality for each solution",
            "Calculate expected benefits per solution",
            "Calculate expected costs per solution",
            "Calculate expected harms per solution",
            "Create Ideality Plot",
            "Categorize solutions (Implement/Improve/Research/Park)",
            "Select top 3 solutions",
            "Research implementation requirements",
            "Create implementation timeline",
            "Generate final synthesis with evidence"
        ]
        for i, title in enumerate(phase6_titles, 51):
            steps.append(TRIZStep(
                step_number=i,
                phase=TRIZPhase.RANK_IMPLEMENT,
                title=title,
                status=StepStatus.PENDING,
                triz_tool="Ideality Plot + Implementation"
            ))
        
        return steps
    
    def _generate_step_instruction(
        self,
        step_num: int,
        problem: str,
        accumulated_knowledge: Dict[str, Any]
    ) -> StepInstruction:
        """Generate instruction for specific step"""
        from .guided_steps import (
            phase1_understand_scope,
            phase2_define_ideal,
            phase3_function_analysis,
            phase4_select_tools,
            phase5_generate_solutions,
            phase6_rank_implement
        )
        
        if 1 <= step_num <= 10:
            return phase1_understand_scope.generate(step_num, problem, accumulated_knowledge)
        elif 11 <= step_num <= 16:
            return phase2_define_ideal.generate(step_num, problem, accumulated_knowledge)
        elif 17 <= step_num <= 26:
            return phase3_function_analysis.generate(step_num, problem, accumulated_knowledge)
        elif 27 <= step_num <= 32:
            return phase4_select_tools.generate(step_num, problem, accumulated_knowledge)
        elif 33 <= step_num <= 50:
            return phase5_generate_solutions.generate(step_num, problem, accumulated_knowledge)
        elif 51 <= step_num <= 60:
            return phase6_rank_implement.generate(step_num, problem, accumulated_knowledge)
        else:
            raise ValueError(f"Invalid step number: {step_num}")
    
    # IMPLEMENT ALL OTHER METHODS:
    # - _validate_findings
    # - _update_accumulated_knowledge
    # - _update_triz_artifacts
    # - _generate_final_solution
    # - _generate_session_summary
    # - _format_instruction
    # - _get_phase_description
    # - _get_phase_progress
    # - _save_session
    # - _load_session


# Public API
def start_guided_triz_research(problem: str) -> Dict[str, Any]:
    """Start guided TRIZ session"""
    solver = GuidedTRIZSolver()
    return solver.start_guided_session(problem)


def submit_research_findings(session_id: str, findings: Dict[str, Any]) -> Dict[str, Any]:
    """Submit findings and get next step"""
    solver = GuidedTRIZSolver()
    return solver.submit_research(session_id, findings)
```

**Critical Implementation Details:**

1. **_validate_findings:** Must check ALL extract_requirements are present
2. **_update_triz_artifacts:** Must populate NineBoxes, Ideality, FunctionMap, etc. from findings
3. **Session persistence:** JSON save/load with full dataclass serialization
4. **Error handling:** Graceful failures with helpful hints
5. **Progress tracking:** Phase and overall progress percentages

---

### TASK 4: Create MCP Handler

**File:** `src/claude_tools/guided_handler.py`

```python
"""
MCP Handler for Guided TRIZ Research
Handles triz_research_start and triz_research_submit tools
"""

from typing import Dict, Any
from triz_tools.models import TRIZToolResponse
from triz_tools.guided_triz_solver import (
    start_guided_triz_research,
    submit_research_findings
)


def handle_research_start(problem: str) -> TRIZToolResponse:
    """
    Start guided TRIZ research session
    
    Args:
        problem: Problem description
        
    Returns:
        TRIZToolResponse with session_id and first step instructions
    """
    try:
        result = start_guided_triz_research(problem)
        
        formatted_instruction = f"""
# 🚀 TRIZ GUIDED RESEARCH SESSION STARTED

**Session ID:** {result['session_id']}
**Total Steps:** {result['total_steps']}
**Current Step:** {result['current_step']}/60
**Phase:** {result['phase']} - {result['phase_description']}

---

## 📋 YOUR RESEARCH TASK (Step {result['current_step']}):

**{result['instruction']['task']}**

### 🔍 Search These in Knowledge Base:
{chr(10).join(f"- {q}" for q in result['instruction']['search_queries'])}

### 📊 Extract These from Research:
{chr(10).join(f"- {r}" for r in result['instruction']['extract'])}

### ✅ Validation Criteria:
{result['instruction']['validation']}

### 📝 Expected Output Format:
```json
{result['instruction']['format']}
```

### 💡 Why This Matters:
{result['instruction']['why']}

### 🎯 TRIZ Tool:
{result['instruction'].get('related_triz_tool', 'N/A')}

---

**Progress:** {result['context']['progress']}

**IMPORTANT:** Submit your findings using `triz_research_submit` with session_id and findings dictionary.
        """
        
        return TRIZToolResponse(
            success=True,
            message=f"TRIZ research session started: {result['session_id']}",
            data={
                "formatted_output": formatted_instruction,
                "session_id": result['session_id'],
                "current_step": result['current_step'],
                "instruction": result['instruction']
            }
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to start TRIZ research: {str(e)}",
            data={}
        )


def handle_research_submit(
    session_id: str,
    findings: Dict[str, Any]
) -> TRIZToolResponse:
    """
    Submit research findings and get next step
    
    Args:
        session_id: Session ID from start
        findings: Research findings dictionary
        
    Returns:
        TRIZToolResponse with validation and next step (or final solution)
    """
    try:
        result = submit_research_findings(session_id, findings)
        
        if not result["success"]:
            # Validation failed
            return TRIZToolResponse(
                success=False,
                message=result["error"],
                data={
                    "hint": result.get("hint", ""),
                    "instruction": result["instruction"],
                    "progress": result["progress"]
                }
            )
        
        if result.get("completed"):
            # Final step completed
            formatted_output = f"""
# ✅ TRIZ RESEARCH COMPLETED!

**Total Steps Completed:** {result['total_steps']}
**Session ID:** {session_id}

---

## 🎯 FINAL SOLUTION

{self._format_final_solution(result['final_solution'])}

---

## 📊 SESSION SUMMARY

{self._format_session_summary(result['session_summary'])}

---

## 🔬 TRIZ ARTIFACTS

{self._format_triz_artifacts(result['triz_artifacts'])}
            """
            
            return TRIZToolResponse(
                success=True,
                message="TRIZ research completed successfully",
                data={
                    "formatted_output": formatted_output,
                    "final_solution": result['final_solution'],
                    "session_summary": result['session_summary']
                }
            )
        
        # Next step
        formatted_instruction = f"""
# ✅ Step {result['step_completed']} Validated!

**Validation:** {result['validation']}

---

## 📋 NEXT RESEARCH TASK (Step {result['current_step']}/60):

**Phase:** {result['phase']} - {result['phase_description']}
**Progress:** {result['progress']}
**Phase Progress:** {result.get('phase_progress', 'N/A')}

---

**{result['instruction']['task']}**

### 🔍 Search These:
{chr(10).join(f"- {q}" for q in result['instruction']['search_queries'])}

### 📊 Extract These:
{chr(10).join(f"- {r}" for r in result['instruction']['extract'])}

### ✅ Validation:
{result['instruction']['validation']}

### 📝 Format:
```json
{result['instruction']['format']}
```

### 💡 Why:
{result['instruction']['why']}
        """
        
        return TRIZToolResponse(
            success=True,
            message=f"Step {result['step_completed']} completed. Moving to step {result['current_step']}",
            data={
                "formatted_output": formatted_instruction,
                "current_step": result['current_step'],
                "progress": result['progress'],
                "instruction": result['instruction']
            }
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to submit research: {str(e)}",
            data={}
        )


def _format_final_solution(solution: Dict[str, Any]) -> str:
    """Format final solution for display"""
    # IMPLEMENT: Format the final solution nicely
    pass


def _format_session_summary(summary: Dict[str, Any]) -> str:
    """Format session summary for display"""
    # IMPLEMENT: Format session summary
    pass


def _format_triz_artifacts(artifacts: Dict[str, Any]) -> str:
    """Format TRIZ artifacts for display"""
    # IMPLEMENT: Format 9 Boxes, Ideality, Function Map, etc.
    pass
```

---

### TASK 5: Update MCP Server

**File:** `src/claude_mcp_server.py`

**Add these tools:**

```python
Tool(
    name="triz_research_start",
    description="Start guided TRIZ research session with 60-step iterative methodology. This tool DOES NOT solve your problem directly. Instead, it guides you through systematic research in 60 steps across 6 phases: (1) Understand & Scope with 9 Boxes + Ideality Audit, (2) Define Ideal Outcome + Resources, (3) Function Analysis (Subject-Action-Object) + Contradictions, (4) Select appropriate TRIZ tools, (5) Generate Solutions using 40 Principles + 76 Standard Solutions + Effects Database + 8 Trends + Materials Research, (6) Rank by Ideality Plot + Implementation. Each step returns specific research instructions. You must search knowledge base, extract information, and submit findings. The tool validates your findings and provides next step. This is the COMPLETE academic TRIZ methodology requiring 60 iterations. For materials problems, Steps 47-49 perform deep research through 44+ engineering books extracting densities, strengths, formability, and creating comparison tables. IMPORTANT: This is a learning process - you discover the solution through guided research, not receive it directly.",
    inputSchema={
        "type": "object",
        "properties": {
            "problem": {
                "type": "string",
                "description": "Detailed problem description. Include: what you're trying to achieve, current limitations, constraints, available resources, and success criteria. More detail = better guidance.",
            }
        },
        "required": ["problem"],
    },
),

Tool(
    name="triz_research_submit",
    description="Submit research findings for current TRIZ research step and receive next step instructions (or final solution if step 60). You must provide findings dictionary matching the extract_requirements from previous step's instruction. The tool validates your findings - if validation fails, you'll receive hints and must research again. If validation succeeds, you receive next step instructions. This continues for all 60 steps. The final step (60) returns complete TRIZ solution with all evidence from your research.",
    inputSchema={
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "Session ID from triz_research_start",
            },
            "findings": {
                "type": "object",
                "description": "Research findings dictionary with keys matching extract_requirements from current step instruction. Must include all required fields with detailed information from knowledge base research.",
            }
        },
        "required": ["session_id", "findings"],
    },
),
```

**Add handlers in `call_tool`:**

```python
elif name == "triz_research_start":
    from claude_tools.guided_handler import handle_research_start
    problem = arguments.get("problem")
    if not problem:
        return [TextContent(type="text", text="Error: problem is required")]
    result = await run_sync(handle_research_start, problem)
    
elif name == "triz_research_submit":
    from claude_tools.guided_handler import handle_research_submit
    session_id = arguments.get("session_id")
    findings = arguments.get("findings")
    if not session_id or not findings:
        return [TextContent(type="text", text="Error: session_id and findings are required")]
    result = await run_sync(handle_research_submit, session_id, findings)
```

---

### TASK 6: Testing

**Create:** `tests/test_guided_triz_complete.py`

**Test scenarios:**
1. Start session → verify Step 1 instruction
2. Submit Step 1 findings → verify Step 2 instruction
3. Submit invalid findings → verify validation failure
4. Complete all 60 steps → verify final solution
5. Test materials problem → verify Steps 47-49 use materials books
6. Test contradiction problem → verify Steps 23-24, 29, 33-40
7. Session persistence → save, load, continue

---

## SUCCESS CRITERIA

The implementation is COMPLETE when:

1. ✅ All 60 steps have detailed instructions (phases 5 & 6 remaining)
2. ✅ GuidedTRIZSolver engine fully implements 60-step workflow
3. ✅ MCP tools work: start session → 60 iterations → final solution
4. ✅ Validation works: rejects incomplete findings with hints
5. ✅ All TRIZ artifacts populated: 9 Boxes, Ideality, Function Map, Contradictions, Solutions
6. ✅ Materials problems trigger deep books research (Steps 47-49)
7. ✅ Final solution includes complete evidence from all steps
8. ✅ Tests pass for complete 60-step flow

---

## CRITICAL NOTES FOR IMPLEMENTER

### DO NOT:
- ❌ Create "simplified" or "concentrated" versions
- ❌ Skip steps or combine steps
- ❌ Make instructions vague or short
- ❌ Generate solutions directly - only instructions
- ❌ Reduce search queries to 1-2 (need 4-5 minimum)
- ❌ Reduce extract_requirements to 1-2 (need 4-5 minimum)

### DO:
- ✅ Follow exact pattern from phases 1-4
- ✅ Every step is equally detailed
- ✅ Use accumulated_knowledge from previous steps
- ✅ Provide realistic example JSON in expected_output_format
- ✅ Explain why_this_matters comprehensively
- ✅ Reference specific TRIZ tools
- ✅ Build upon previous findings progressively
- ✅ Validate findings thoroughly

### REFERENCE FILES:
- **Template:** `src/triz_tools/guided_steps/phase1_understand_scope.py`
- **Data Models:** `src/triz_tools/triz_models.py`
- **Academic Paper:** See context in CLAUDE.md
- **TRIZ Documentation:** Complete TRIZ methodology documentation provided

---

## ESTIMATED EFFORT

- Phase 5 instructions (18 steps): **4-6 hours**
- Phase 6 instructions (10 steps): **2-3 hours**  
- Complete solver engine: **4-6 hours**
- MCP handler: **2-3 hours**
- Testing: **2-4 hours**

**Total: 14-22 hours of focused development**

---

## DELIVERY

When complete, commit with message:
```
feat: Complete TRIZ guided solver with 60-step methodology

- Implement Phase 5 instructions (Steps 33-50): Solution Generation
- Implement Phase 6 instructions (Steps 51-60): Ranking & Implementation  
- Complete GuidedTRIZSolver engine with full 60-step workflow
- Add triz_research_start and triz_research_submit MCP tools
- Implement guided_handler for MCP integration
- Add comprehensive testing for 60-step flow
- Full TRIZ methodology: 9 Boxes, Ideality, Function Analysis, 
  40 Principles, 76 Standard Solutions, Effects, 8 Trends
```

---

## QUESTIONS?

If anything is unclear:
1. Look at phases 1-4 implementation as templates
2. Refer to `triz_models.py` for all data structures
3. Follow academic TRIZ methodology in documentation
4. Each step must guide AI to DISCOVER solution, not give it

**The goal: AI performs 60 iterations of research and discovers the solution through guided TRIZ methodology.**
